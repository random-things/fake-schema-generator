# Table of Contents for Fake Schema Generator

Current release version: N/A  
Current development version: [v0.1.0](#v010)  


* [Versions](#versions)
  * [v0.1.0](#v010)
* [Roadmap](#roadmap)
  * [Next version](#next-version)
  * [Future versions](#future-versions)

## Versions

* [v0.1.1](#v011) - 2024-05-03
* [v0.1.0](#v010) - 2024-05-02

### v0.1.1
* 🐛 Fixed several places where functions expected `type[dataclass]`, but were hinted with `dataclass` instead
* ♻️ Removed several instances where entire modules or packages were being imported instead of specific members
* ♻️ Eliminate the requirement to access "protected" members of `FakeSchemaGenerator`
  * ✨ Added a `data` method on `FakeSchemaGenerator` to return the generated data
  * ♻️ Made `FakeSchemaGenerator._register` public as `FakeSchemaGenerator.register`
* ♻️ Added a `FakeSchemaGenerator.generate` method as a convenience wrapper for `FakeSchemaGenerator.generate_from_dag`
* ♻️ Modified `SequentialNumberProvider.reset_sequence` to reset all sequences by default instead of one namespace
* 📝 Documented classes and functions with docstrings, [README.md](README.md) is no longer the only documentation

### v0.1.0
* 🐛 `operator.add` and `operator.mul` take two arguments, replaced with `typed_sum` and `typed_product`
* 📝 Adding a changelog
* 📝 Writing documentation and adding a license
* ♻️ Refactoring `SchemaCondition` parameter order to be more intuitive
* ♻️ Refactoring `_model_str_to_model` to search cached models before inspecting frames
* 🎉 Initial release

## Roadmap

### Next version

* 📦 Package for distribution

### Future versions

* ♻️ Support more complex calculations in `calculate`, specifically allowing AND/OR
* ✨ Add support for Pydantic dataclasses and validations

### Future possibilities

* ♻️ Syntactic sugar for `SchemaCondition`, e.g., `SchemaCondition[Model.Field == OtherModel.Field]
* ♻️ Add a `ProviderGenerator` to `FakeSchemaGenerator` to get rid of intermediate `Provider` classes that just 
  forward calls to faker
* ♻️ Update `ProductNameGenerator` to generate more plausible product names
* ♻️ Add a way to ensure that each row in a table has at least one corresponding row in another table
  * Specifically, when generating the example schema, there are 100 `Order`s, but many of them have no associated
    `OrderProducts`. However, in a real database, each `Order` would have at least one `OrderProduct`.
* 🧪 Decide if I care that tests still use protected members of `FakeSchemaGenerator`