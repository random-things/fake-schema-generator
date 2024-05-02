# Table of Contents for Fake Schema Generator

Current release version: N/A  
Current development version: [v0.1.0](#v010)  


* [Versions](#versions)
  * [v0.1.0](#v010)
* [Roadmap](#roadmap)
  * [Next version](#next-version)
  * [Future versions](#future-versions)

## Versions

* [v0.1.0](#v010) - 2024-05-02

### v0.1.0
* 📝 Adding a changelog
* 📝 Writing documentation and adding a license
* ♻️ Refactoring `SchemaCondition` parameter order to be more intuitive
* ♻️ Refactoring `_model_str_to_model` to search cached models before inspecting frames
* 🎉 Initial release

## Roadmap

### Next version

* ♻️ Eliminate the requirement to access "protected" members of `FakeSchemaGenerator`
* 📦 Package for distribution

### Future versions

* ♻️ Support more complex calculations in `calculate`, specifically allowing AND/OR
* ✨ Add support for Pydantic dataclasses and validations

### Future possibilities

* ♻️ Syntactic sugar for `SchemaCondition`, e.g., `SchemaCondition[Model.Field == OtherModel.Field]
* ♻️ Add a `ProviderGenerator` to `FakeSchemaGenerator` to get rid of intermediate `Provider` classes that just 
  forward calls to faker
* ♻️ Update `ProductNameGenerator` to generate more plausible product names