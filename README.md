# OPC Metadata App

## Purpose

This Streamlit app collects structured metadata from OPC teams via a fillable online form and writes each record as a canonical JSON file conforming to `master_OPC_schema.json`. The JSON files (per OPC) are the single source of truth. Additional tables can be derived from them on demand.

Both the app and the JSON schema are prototypes for storing MARVIC OPC metadata in a standardized and machine-accessible way.

---

## 1. About the app

Eight pages, each mapping to one schema section:

| Page                         | Schema section edited                    |
| ---------------------------- | ---------------------------------------- |
| Home / OPC selector          | `record_metadata`                        |
| Factsheet                    | `factsheet`                              |
| Models                       | `models`                                 |
| Uncertainty propagation      | `uncertainty_propagation`                |
| Validation evidence overview | `validation_evidence_overview`           |
| CRCF model readiness matrix  | `crcf_model_readiness_matrix`            |
| Review & validate            | full record (read-only, not implemented) |
| Export                       | derived outputs                          |

Session state persists the loaded record across all pages.

---

## 2. App folder structure

```
opc_dashboard/
├── app.py                          # Home / OPC selector; edits record_metadata
├── pages/
│   ├── 01_factsheet.py
│   ├── 02_models.py
│   ├── 03_uncertainty_propagation.py
│   ├── 04_validation_evidence.py
│   ├── 05_crcf_matrix.py
│   ├── 06_review_validate.py       # pseudocode, not implemented
│   └── 07_export.py
├── core/
│   ├── schema.py                   # Loads master_OPC_schema.json from disk
│   ├── defaults.py                 # Blank record + default CRCF rows
│   ├── state.py                    # Session state helpers
│   ├── validation.py               # Schema + business-rule validation
│   ├── storage.py                  # Atomic JSON load/save; auto-stamps last_updated
│   ├── flatten.py                  # JSON -> 5 CSV tables
│   └── enums.py                    # Controlled vocabularies (derived from schema)
├── data/
│   ├── master_OPC_schema.json      # Authoritative schema (symlink or copy)
│   ├── opc_records/
│   │   ├── example_hybrid_arable_opc.json
│   │   └── ...
│   └── exports/
│       ├── opc_factsheet.csv
│       ├── opc_models.csv
│       ├── opc_uncertainty_propagation.csv
│       ├── opc_validation_evidence_overview.csv
│       └── opc_crcf_model_readiness_matrix.csv
└── .streamlit/
    └── config.toml
```

---

## 3. Usage principle

**Main idea:** Use JSON as the canonical store and treat the UI as an editor for that JSON.

There are some example CSVs that are derived outputs. Both the OPC json and the example tables can be exported from the app on the Export Page.

### Export page

**Purpose:** preview and download the five output tables.

**Actions:**

- **Download current OPC JSON** -- `st.download_button` for the in-memory record
- **Regenerate all CSV exports** -- calls `export_all_csvs()` across all JSON files in `data/opc_records/`
- **Preview tables** -- `st.tabs` for each of the five tables with `st.dataframe`

**Tables produced** (with exact column names):

| Output file                            | Key columns                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `opc_factsheet.csv`                    | `opc_id`, `opc_name`, `opc_fullname`, `lead_institutions`\*, `main_modelling_approach`, `target_lusts`\*, `geographic_focus`\*, `ghgs_covered`\*, `cf_practices_covered`\*, `reporting_scale`\*, `update_frequency`, `user_orientation`\*, `operational_maturity`, `openness_level`, `validation_status`, `validation_status_notes`, `execution_targets`\*, `containerised`, `container_tech`\*, `requires_parallelisation`, `minimum_compute_notes`, `schema_version`, `last_updated` |
| `opc_models.csv`                       | `opc_id`, `opc_name`, `row_index`, `model_name`, `model_role`, `model_version`, `model_repository`, `scientific_publication_dois`\*, `model_notes`                                                                                                                                                                                                                                                                                                                                     |
| `opc_uncertainty_propagation.csv`      | `opc_id`, `opc_name`, then for each of the 6 sources: `<source>_count`, `<source>_data_driven`, `<source>_top_inputs`\*, `<source>_propagated`, `<source>_method` (30 columns), plus `project_scale` — one row per OPC                                                                                                                                                                                                                                                                 |
| `opc_validation_evidence_overview.csv` | `opc_id`, `opc_name`, `row_index`, `variable_validated`, `dataset_type`, `geography`, `period`, `validation_metrics`\*, `summary_result`, `remaining_gap`                                                                                                                                                                                                                                                                                                                              |
| `opc_crcf_model_readiness_matrix.csv`  | `opc_id`, `opc_name`, `assessment_unit`, `applies_to_model_name`, `eligibility_national_inventory_model`, `eligibility_commission_compliant_model`, `criterion_code`, `criterion_label`, `status`, `short_justification`, `priority_for_improvement`, `evidence_notes`, `min_accuracy_bias_lte_pmu`, `min_accuracy_pi_90pct`, `min_accuracy_r2_gt_0` — 4 rows per OPC (one per compliance criterion)                                                                                   |

\* Semicolon-separated in the CSV cell.

---

## 4. How to develop

### Running the app

Navigate to the repository root (the folder that contains `opc_dashboard/` and `master_OPC_schema.json`), then launch Streamlit. The exact command depends on how you manage your Python environment:

```bash
# standard venv or conda (activate your environment first)
streamlit run opc_dashboard/app.py

# explicit python invocation
python -m streamlit run opc_dashboard/app.py
```

Required packages: `streamlit`, `jsonschema`, `pandas`. Install them with whichever tool your environment uses (e.g. `pip install streamlit jsonschema pandas` or via a `requirements.txt` / `pyproject.toml`).

> [!WARNING]
> Add a `.gitignore` and do not commit real OPC records or generated CSVs under `data/opc_records/` or `data/exports/`. The files currently checked in are illustrative examples only.

---

### Adding a new field to an existing section

When you add a field to any part of the data model, touch these files **in order**:

1. **`master_OPC_schema.json`**: add the field here first. This is the single source of truth.

   - Choose the right type (`string`, `boolean`, `array`, …).
   - If the field has a fixed vocabulary, add an `"enum"` list.
   - If the field is optional (no user input required), do **not** add it to `"required"`. If it is mandatory, add it there.
   - If the type is `string` and an empty value `""` is a valid intermediate state (e.g. an optional text box a user may leave blank), use `{"type": "string"}` — not `{"$ref": "#/$defs/nonEmptyString"}`. Reserve `nonEmptyString` only for fields that must be filled before saving.

2. **`core/enums.py`**: if the field has an `enum` in the schema, derive the list here so widgets stay in sync automatically. Follow the existing pattern of reading from `_schema["properties"][...]["enum"]`. Don't hardcode enum values in page files but always import from `enums.py`.

3. **`core/defaults.py`**: add a sensible default value for the new field inside `new_opc_record()`. This ensures blank records created through the UI are always schema-valid from the start. For booleans use `False`, for strings `""`, for arrays `[]`. If the field belongs to a nested sub-structure (like the CRCF criteria detail), update the relevant helper function (e.g. `default_crcf()`) as well.

4. **The page file** (`pages/0N_<section>.py`): add the appropriate Streamlit widget and wire it up to read from and write back to the record slice. Import enum lists from `enums.py` rather than redefining them locally.

5. **`core/flatten.py`**: add the field to the relevant `flatten_*` function so it appears in the exported CSV. For array fields, wrap with `_join(...)` to produce semicolon-separated output.

6. **`core/validation.py`**: consider whether the new field introduces any cross-field business rules that the schema alone cannot express (e.g. "if field A has value X, field B must be non-empty"). Add them to `validate_business_rules()` as non-blocking warnings.

7. **Existing JSON data files** in `opc_dashboard/data/opc_records/`: if the new field is required by the schema, add it to every existing file. If it is optional, existing files will still validate without it, but you may want to add a placeholder for completeness. Run the validation script below to check.

8. **Documentation**: update this README and maybe create a `CHANGELOG.md` to reflect the new field.

---

### Adding a new page

1. Create `opc_dashboard/pages/0N_<name>.py`. Follow the existing page structure: call `_s.ensure_session_state()`, guard with `_s.is_loaded()`, read the relevant record slice, display widgets, save on button press.

2. Register the page in **`opc_dashboard/app.py`** by adding a `st.Page(...)` entry to the `st.navigation([...])` list in the correct position.

3. If the new page writes to a new top-level key in the record, add that key to `master_OPC_schema.json`, `defaults.py`, `flatten.py`, and `validation.py` following the field checklist above.

---

### Module responsibilities at a glance

| Module                   | Purpose                                               | Update when…                                        |
| ------------------------ | ----------------------------------------------------- | --------------------------------------------------- |
| `master_OPC_schema.json` | Defines every valid field, type, and constraint       | Adding, removing, or changing any field             |
| `core/enums.py`          | Derives controlled-vocabulary lists from the schema   | A new `enum` field is added to the schema           |
| `core/defaults.py`       | Provides blank record templates for new OPCs          | A new required or sensibly defaulted field is added |
| `core/flatten.py`        | Converts JSON records to CSV rows                     | Any field that should appear in an exported CSV     |
| `core/validation.py`     | Checks schema validity and cross-field business rules | A new cross-field constraint is needed              |
| `core/state.py`          | Session state accessors (rarely changed)              | The set of top-level session state keys changes     |
| `core/storage.py`        | Atomic JSON load/save (rarely changed)                | The file layout or naming convention changes        |
| `core/schema.py`         | Loads the schema from disk (rarely changed)           | The schema file moves                               |
