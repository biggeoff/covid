import os
import argparse
import pandas as pd


cols=[
    'central_sample_id','adm1', 'received_date', 'collection_date', 
    'source_age', 'source_sex', 'is_surveillance', 'collection_pillar', 
    'is_hcw', 'employing_hospital_name', 'employing_hospital_trust_or_board', 
    'is_hospital_patient', 'is_icu_patient', 'admitted_with_covid_diagnosis', 
    'admission_date', 'admitted_hospital_name', 'admitted_hospital_trust_or_board', 
    'is_care_home_worker', 'is_care_home_resident', 'anonymised_care_home_code', 
    'adm2', 'adm2_private', 'biosample_source_id', 'root_sample_id', 
    'sender_sample_id', 'collecting_org', 'sample_type_collected', 
    'sample_type_received', 'swab_site', 'epi_cluster', 'investigation_name', 
    'investigation_site', 'investigation_cluster', 'majora_credit', 
    'ct_1_ct_value', 'ct_1_test_target', 'ct_1_test_platform', 
    'ct_1_test_kit', 'ct_2_ct_value', 'ct_2_test_target', 'ct_2_test_platform',
    'ct_2_test_kit', 'sequencing_org_received_date', 'library_name', 
    'library_seq_kit', 'library_seq_protocol', 'library_layout_config', 
    'library_selection', 'library_source', 'library_strategy', 'library_layout_insert_length', 
    'library_layout_read_length', 'barcode', 'artic_primers', 'artic_protocol', 'run_name', 
    'instrument_make', 'instrument_model', 'start_time', 'end_time', 'flowcell_id', 
    'flowcell_type', 'bioinfo_pipe_name', 'bioinfo_pipe_version']



if __name__ == "__main__":
    args=parseArgs()
    cases = parseClimbDirectory(args.climbdir[0])
    
    data.to_csv(args.output[0])