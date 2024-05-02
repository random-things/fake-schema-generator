import random
from collections import deque
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import fields as dataclass_fields
from dataclasses import is_dataclass
from inspect import Parameter
from inspect import Signature
from inspect import currentframe
from inspect import signature
from types import MappingProxyType
from typing import Any
from typing import Callable
from typing import Optional

from faker import Faker

from fake_schema_generator.fake_types.FakeType import FakeType
from fake_schema_generator.fake_types.SchemaCondition import SchemaCondition
from fake_schema_generator.fake_types.ValueOf import ValueOf
from fake_schema_generator.functions import dataclass_to_interface
from fake_schema_generator.functions import extract_annotations
from fake_schema_generator.operators import noop
from fake_schema_generator.providers import CalculateProvider
from fake_schema_generator.providers import ProductNameProvider
from fake_schema_generator.providers import ReferenceProvider
from fake_schema_generator.providers import SequentialNumberProvider


class FakeSchemaGenerator:
    def __init__(self):
        self._dependent_fake_providers: set[str] = set()
        self._fake = Faker()
        self._fake.add_provider(SequentialNumberProvider)
        self._fake.add_provider(ProductNameProvider)
        calc_provider = CalculateProvider(self._fake, self)
        ref_provider = ReferenceProvider(self._fake, self)
        self._add_referring_provider(calc_provider.reference_functions)
        self._add_referring_provider(ref_provider.reference_functions)
        self._fake.add_provider(calc_provider)
        self._fake.add_provider(ref_provider)

        self._annotations: dict[dataclass, dict[str, Any]] = {}
        self._data: dict[str, list[dataclass]] = {}
        self._raw_data: dict[str, list[dataclass]] = {}
        self._models: dict[str, dataclass] = {}
        self._interfaces: dict[str, dataclass] = {}
        self._instances: dict[str, list[dataclass]] = {}
        self._field_dag: list[tuple[str, str]] = []
        self._field_dependencies: dict[tuple[str, str], set[tuple[str, str]]] = {}
        self._model_dependencies: dict[str, set[str]] = {}
        self._field_populated: dict[tuple[str, str], bool] = {}

    @staticmethod
    def _has_field(cls: dataclass, field: str) -> bool:
        return field in [f.name for f in dataclass_fields(cls)]

    @staticmethod
    def _has_keyword_argument(func: Callable, kwarg: str) -> bool:
        sig: Signature = signature(func)
        params: MappingProxyType[str, Parameter] = sig.parameters
        has_argument = (kwarg in params and params[kwarg].default is not Parameter.empty) or any(
            p.kind == Parameter.VAR_KEYWORD for p in params.values()
        )
        return has_argument

    def _add_referring_provider(self, functions: set[str]):
        self._dependent_fake_providers.update(functions)

    def _build_field_dag(self):
        schema = self._field_dependencies

        # First, remove independent tables from the schema.
        independent_tables = {table for table in self._model_dependencies if len(self._model_dependencies[table]) == 0}

        # Step 1: Build the graph
        in_degree = {key: 0 for key in schema}  # Initialize in-degree of each node
        adjacency_list = {key: [] for key in schema}  # Initialize adjacency list

        # Populate in-degree and adjacency list
        for node, dependencies in schema.items():
            for dep in dependencies:
                adjacency_list[dep].append(node)
                in_degree[node] += 1

        # Step 2: Topological Sort using Kahn's algorithm
        # Start with nodes with no incoming edges (in_degree = 0)
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        ordered_fields = []

        while queue:
            node = queue.popleft()
            ordered_fields.append(node)
            # For each node this node points to, reduce its in-degree
            for dependent in adjacency_list[node]:
                in_degree[dependent] -= 1
                # If in-degree becomes 0, add it to the queue
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check if there was a cycle (not all nodes were processed)
        if len(ordered_fields) != len(schema):
            raise ValueError("There is a cycle in the dependencies, cannot perform topological sort.")

        # Move fields from independent tables to the front of the list.
        sorted_fields = [f for f in ordered_fields if f[0] in independent_tables]
        # Then add the fields with no dependencies.
        sorted_fields += [f for f, d in self._field_dependencies if f not in sorted_fields and len(d) == 0]
        # Finally, add the rest in their sorted order.
        sorted_fields += [f for f in ordered_fields if f[0] not in independent_tables and f not in sorted_fields]

        self._field_dag = sorted_fields

    def _build_field_dependencies(self):
        models_to_register: set[dataclass] = set()
        for model in self._models.values():
            for field in dataclass_fields(model):
                self._field_populated[(model.__name__, field.name)] = False
                if len(self._annotations[model.__name__][field.name]["metadata"]) > 0:
                    fake_type = next(
                        filter(
                            lambda x: isinstance(x, FakeType),
                            self._annotations[model.__name__][field.name]["metadata"],
                        ),
                        None,
                    )
                    current_field: tuple[str, str] = (model.__name__, field.name)
                    if fake_type and fake_type.type in self._dependent_fake_providers:
                        if current_field not in self._field_dependencies:
                            self._field_dependencies[current_field] = set()
                        fields: list[str] = [
                            fake_type.kwargs.get("field"),
                            *fake_type.kwargs.get("fields", []),
                        ]
                        for f in fields:
                            if len(f) > 0:
                                if fake_type.kwargs["model"] not in self._models:
                                    models_to_register.add(self._model_str_to_model(fake_type.kwargs["model"]))
                                depends_on: tuple[str, str] = (
                                    fake_type.kwargs["model"],
                                    f,
                                )
                                self._field_dependencies[current_field].add(depends_on)
                    else:
                        self._field_dependencies[current_field] = set()

        if len(models_to_register) > 0:
            for model in models_to_register:
                self._register(model)
                self._model_dependencies[model.__name__] = set()
            self._build_field_dependencies()

    def _build_model_dependencies(self):
        self._build_field_dependencies()

        # Iterate through the field DAG and build the model DAG.
        # First, find models with no dependencies.
        for k, v in self._field_dependencies.items():
            model, field = k
            if model not in self._model_dependencies:
                self._model_dependencies[model] = set()
            if len(v) >= 0:
                for inner_model, inner_field in v:
                    self._model_dependencies[model].add(inner_model)

        self._build_field_dag()

    def _model_str_to_model(self, model_str: str) -> dataclass:
        # Easiest path forward.
        if model_str in self._models:
            model: dataclass = self._models.get(model_str, None) or globals()[model_str]
            if is_dataclass(model):
                return model
            else:
                raise ValueError(f"Model {model_str} is not a dataclass")

        # Otherwise, we have to search the frames...
        frame = currentframe()
        try:
            while frame.f_back:
                if model_str in frame.f_globals:
                    model: dataclass = frame.f_globals[model_str]
                    if is_dataclass(model):
                        return model
                else:
                    new_frame = frame.f_back
                    del frame
                    frame = new_frame
        finally:
            del frame

        raise ValueError(f"Model {model_str} not found")

    def _register[T](self, model: type[T]) -> None:
        if model.__name__ not in self._models:
            self._annotations[model.__name__] = extract_annotations(model)
            self._models[model.__name__] = model
            self._interfaces[model.__name__] = dataclass_to_interface(model)
            self._data[model.__name__] = []
            self._raw_data[model.__name__] = []

    def calculate(
        self,
        source_model: dataclass,
        model: type[dataclass] | str,
        field: str,
        value: Any,
        fields: list[str],
        row_op: Optional[Callable] = noop,
        col_op: Optional[Callable] = noop,
    ) -> Any:
        if len(fields) == 0:
            raise ValueError("At least one field is required")

        if isinstance(model, str):
            model = self._model_str_to_model(model)

        if field and not self._has_field(model, field):
            raise ValueError(f"Field {field} not found in model {model.__name__}")

        for f in fields:
            if not self._has_field(model, f):
                raise ValueError(f"Field {f} from fields not found in model {model.__name__}")

        value = getattr(source_model, value.field) if isinstance(value, ValueOf) else value

        rows: list[model] = [
            instance for instance in self._instances[model.__name__] if getattr(instance, field) == value
        ]
        rows += [r for r in self._raw_data[model.__name__] if r == value]

        if len(rows) == 0:
            return 0
        else:
            col_values = []
            for instance in rows:
                row_values = [getattr(instance, f) for f in fields]
                row_value = row_op(*row_values)
                col_values.append(row_value)
            if len(col_values) == 1:
                return col_values[0]
            else:
                return col_op(*col_values)

    def generate_from_dag(self):
        if len(self._model_dependencies) == 0:
            self._build_model_dependencies()

        for field in self._field_dag:
            iter_model, iter_field = field

            if iter_model not in self._instances:
                self._instances[iter_model] = []
                current_instance = self._interfaces[iter_model]()
                self._instances[iter_model].append(current_instance)
            current_instance = self._instances[iter_model][-1]
            fake_type = next(
                filter(
                    lambda x: isinstance(x, FakeType),
                    self._annotations[iter_model][iter_field]["metadata"],
                ),
                None,
            )

            if fake_type and hasattr(self._fake, fake_type.type):
                fn_kwargs: dict[str, Any] = fake_type.kwargs.copy()
                if fake_type.type in self._dependent_fake_providers:
                    fn_kwargs["source_model"] = current_instance
                fn = getattr(self._fake, fake_type.type)
                setattr(current_instance, iter_field, fn(**fn_kwargs))

        for k, v in self._instances.items():
            self._raw_data[k] += [self._models[k](**asdict(i)) for i in v]

    def reference(
        self,
        source_model: dataclass,
        model: type[dataclass] | str,
        field: Optional[Any] = None,
        conditions: Optional[list[SchemaCondition]] = None,
    ) -> Any:
        if isinstance(model, str):
            model = self._model_str_to_model(model)

        if model.__name__ not in self._models:
            self._register(model)

        if field and not self._has_field(model, field):
            raise ValueError(f"Field {field} not found in model {model.__name__}")

        if len(self._raw_data[model.__name__]) == 0 and len(self._instances[model.__name__]) == 0:
            raise ValueError(f"No data found for model {model.__name__}.{field}")

        obj: type[dataclass] | None = None
        if len(self._raw_data[model.__name__]) > 0 or len(self._instances[model.__name__]) > 0:
            combined_data = self._raw_data[model.__name__] + self._instances[model.__name__]
            if field is not None and conditions is not None:
                for instance in combined_data:
                    if all(
                        [
                            cond.comparison(
                                getattr(source_model, cond.field, None),
                                (
                                    getattr(instance, cond.value.field)
                                    if isinstance(cond.value, ValueOf)
                                    else cond.value
                                ),
                            )
                            for cond in conditions
                        ]
                    ):
                        obj = instance
                        break
            elif field is not None:
                obj = random.choice(combined_data)
        else:
            obj = random.choice(self._instances[model.__name__])

        return getattr(obj, field)
