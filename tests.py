# TEST polystat_cond.py
calc_ply = r"C:\JL\Testing\conductivity\Riverscapes\inputs.gdb\catch_test"
out_tbl = r"C:\JL\Testing\conductivity\Riverscapes\outputs\cond_params.dbf"
env_dir = r"C:\JL\ISEMP\Data\ec\model\Grids_rsmp"
rs_bool = "true"
wshd_name = "Entiat"
rs_proj_name = "Predicted Conductivity"
rs_real_name = "Realization Run 01"
rs_dir = r"C:\JL\Testing\conductivity\Riverscapes\rs"

# TEST predict_cond.py
in_fc = r"C:\JL\Testing\conductivity\Riverscapes\inputs.gdb\seg1000m_test"
in_params = r"C:\JL\Testing\conductivity\Riverscapes\outputs\cond_params.dbf"
out_fc = r"C:\JL\Testing\conductivity\Riverscapes\outputs\pred_cond.shp"
rs_bool = "true"
rs_dir = r"C:\JL\Testing\conductivity\Riverscapes\rs"
rs_real_name = "Realization Run 01"