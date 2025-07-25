# Models

## Organizations

```bash
sqlacodegen \
  "postgresql://ajinkya_rds:wozbu9-makton-Sozcic@lunartree-app-db-1.cbyaq6ycc3ii.us-west-2.rds.amazonaws.com:5432/lunartree_stage_1_data_processing" \
  --schema organizations \
  --outfile models/organizations.py
```

## Organization Knowledge

```bash
sqlacodegen \
  "postgresql://ajinkya_rds:wozbu9-makton-Sozcic@lunartree-app-db-1.cbyaq6ycc3ii.us-west-2.rds.amazonaws.com:5432/lunartree_stage_1_data_processing" \
  --schema organization_knowledge \
  --outfile models/organization_knowledge.py
```

## Organization Information

```bash
sqlacodegen \
  "postgresql://ajinkya_rds:wozbu9-makton-Sozcic@lunartree-app-db-1.cbyaq6ycc3ii.us-west-2.rds.amazonaws.com:5432/lunartree_stage_1_data_processing" \
  --schema organization_information \
  --outfile models/organization_information.py
```

## Products

```bash
sqlacodegen \
  "postgresql://ajinkya_rds:wozbu9-makton-Sozcic@lunartree-app-db-1.cbyaq6ycc3ii.us-west-2.rds.amazonaws.com:5432/lunartree_stage_1_data_processing" \
  --schema products \
  --outfile models/products.py
```

# Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Run
```bash
streamlit run main.py
```

