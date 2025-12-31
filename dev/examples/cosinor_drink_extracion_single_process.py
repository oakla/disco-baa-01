import pandas as pd
from datetime import datetime
import os
import warnings
import numpy as np
from scipy.optimize import curve_fit

# Suppress warnings
warnings.filterwarnings('ignore')

# Global configuration (全局配置)
RAW_DATA_DIR = os.getcwd()  # assume raw Excel file is in current directory (假设原始 Excel 文件在当前目录下)
SPLITTED_DATA_DIR = os.path.join(os.getcwd(), "splitted_data_file")
OUTPUT_DIR = os.path.join(os.getcwd(), "processed_cosinor_outputs")
OUTPUT_DRINK_DIR = os.path.join(os.getcwd(), "processed_drink_outputs")
os.makedirs(SPLITTED_DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DRINK_DIR, exist_ok=True)

# Cosinor model function
def cosinor_model(t, M, A, phi):
    T = 24  # Period is 24 hours
    return M + A * np.cos(2 * np.pi * t / T + phi)

# Function to perform cosinor analysis
def perform_cosinor_analysis(temp_data, time_hours):
    try:
        M_guess = temp_data.mean()
        A_guess = (temp_data.max() - temp_data.min()) / 2
        phi_guess = 0
        params, _ = curve_fit(cosinor_model, time_hours, temp_data, p0=[M_guess, A_guess, phi_guess])
        M, A, phi = params
        residuals = temp_data - cosinor_model(time_hours, *params)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((temp_data - temp_data.mean())**2)
        r_squared = 1 - (ss_res / ss_tot)
        return M, abs(A), phi, r_squared
    except Exception as e:
        print(f"⚠️ Cosinor analysis failed: {e}")
        return np.nan, np.nan, np.nan, np.nan

# Function to remove outliers and interpolate data
def remove_outliers_interpolate_drink(data, col_name, abnormal_temp_thresh=35, temp_thresh=-0.5):
    data = data.reset_index()
    filtered_data = data[data[col_name] >= abnormal_temp_thresh]
    filtered_data['Temp_Change'] = filtered_data[col_name].diff()
    filtered_data['Temp_Change_2'] = filtered_data[col_name].diff(2)
    filtered_data['Significant_Drop'] = ((filtered_data['Temp_Change'] < temp_thresh) | (filtered_data['Temp_Change_2'] < temp_thresh))
    filtered_data['Follows_Drop'] = filtered_data['Significant_Drop'].shift(-1) | filtered_data['Significant_Drop'].shift(-2)
    drinking_events = filtered_data[(filtered_data['Significant_Drop']) & (~filtered_data['Follows_Drop'])]

    for idx in drinking_events.index:
        try:
            tmp_drop_data = data.loc[idx - 10: idx + 20][['DT', col_name]].copy()
            if not tmp_drop_data.empty:
                min_index = tmp_drop_data[col_name].idxmin()
                start_max_index = (data.loc[min_index - 10: min_index + 5, col_name]).idxmax()
                end_max_index = (data.loc[min_index: min_index + 20, col_name]).idxmax()
                data.loc[(start_max_index + 1): (end_max_index - 1), col_name] = np.nan
        except Exception as e:
            print(f"⚠️ Error in outlier removal/interpolation for drinking event at index {idx}: {e}")

    data[col_name] = data[col_name].interpolate(method='linear')
    return data

def extract_pointed_temp_value(temp_data, percentage_split):
    try:
        temp_sorted = temp_data.sort_values(ascending=True).reset_index(drop=True)
        temp_sorted_inverse = temp_data.sort_values(ascending=False).reset_index(drop=True)
        n = len(temp_data)
        if n > 0:
            indice = int(percentage_split * n)
            if indice < n:
                return temp_sorted.iloc[indice], temp_sorted_inverse.iloc[indice]
            else:
                return np.nan, np.nan
        else:
            return np.nan, np.nan
    except Exception as e:
        print(f"⚠️ Error extracting pointed temperature value at {percentage_split}: {e}")
        return np.nan, np.nan


def drink_detection(data, col_name, temp_thresh=-1.0):
    data = data.reset_index()
    # Filter out abnormal data, keeping records where temperature is >= 30 degrees
    filtered_data = data[data[col_name] >= 30]

    # Calculate temperature changes to help identify drinking events
    filtered_data['Temp_Change'] = filtered_data[col_name].diff()

    # Define a significant temperature drop (>1 degree within 5 to 10 minutes)
    # This accounts for consecutive readings, considering the data sampling rate (every 5 minutes)
    filtered_data['Temp_Change_2'] = filtered_data[col_name].diff(2)  # Change over 10 minutes
    filtered_data['Significant_Drop'] = (
                (filtered_data['Temp_Change'] < temp_thresh) | (filtered_data['Temp_Change_2'] < temp_thresh))

    # Identify rows immediately following a significant drop, implying temperature begins to stabilize
    filtered_data['Follows_Drop'] = filtered_data['Significant_Drop'].shift(-1) | filtered_data[
        'Significant_Drop'].shift(-2)

    # Select events that represent a significant drop followed by a stabilization
    drinking_events = filtered_data[(filtered_data['Significant_Drop']) & (~filtered_data['Follows_Drop'])]

    res_data_list = []

    for idx in drinking_events.index:
        tmp_drop_data = data.loc[idx - 5: idx + 20][['DT', col_name]]
        # find the minimum value index in a window
        min_index = tmp_drop_data[col_name].idxmin()

        if min_index >= 2:
            temp_before_5min = data.loc[min_index - 1][col_name]
            temp_before_10min = data.loc[min_index - 2][col_name]
        else:
            temp_before_5min = data.loc[min_index][col_name]
            temp_before_10min = data.loc[min_index][col_name]


        start_max_index = (data.loc[min_index - 3: min_index][col_name]).idxmax()
        temp_before_drink = data.loc[start_max_index][col_name]

        end_max_index = (data.loc[min_index: min_index + 30][col_name]).idxmax()
        temp_after_drink_rec = data.loc[end_max_index][col_name]

        tmp_res_df = data.loc[min_index][['DT', col_name]]
        tmp_res_df = pd.DataFrame({
            'DT': [data.loc[min_index]['DT']],
            'drink_temp': [data.loc[min_index][col_name]],
            'before_5min_temp': [temp_before_5min],
            'before_10min_temp': [temp_before_10min],
            'before_drink_temp': [temp_before_drink],
            'after_drink_recover': [temp_after_drink_rec],
            'recover_time': [5 * (end_max_index - min_index)],
            'drop_time': [5 * (min_index - start_max_index)],
            'logger_code': [col_name]
        })

        res_data_list.append(tmp_res_df)

    # Interpolate the data where outliers were found

    if len(res_data_list) == 0:
        return pd.DataFrame()


    res_data = pd.concat(res_data_list)

    return res_data

def process_single_sheep_cosinor(file_path, sheep_id, abnormal_temp_thresh=35, temp_thresh=-0.5, extract_min_max_temp=True):
    """
    Process data for a single sheep from a CSV file.
    """
    try:
        sheep_data = pd.read_csv(file_path)
        if 'DT' not in sheep_data.columns or sheep_id not in sheep_data.columns:
            print(f"⚠️ Missing 'DT' or '{sheep_id}' column in {file_path}. Skipping.")
            return

        sheep_data['DT'] = pd.to_datetime(sheep_data['DT'])
        sheep_data['date'] = sheep_data['DT'].dt.date.astype('str')
        sheep_data['hour'] = sheep_data['DT'].dt.hour.astype('str')
        sheep_data['DataTime'] = sheep_data['DT']
        sheep_data.set_index('DataTime', inplace=True)

        all_cosinor_data = []
        sheep_record_date_list = sorted(sheep_data['date'].unique())
        percent_list = [1, 5, 10, 20, 30, 40, 45] if extract_min_max_temp else []

        for current_date in sheep_record_date_list:
            try:
                condition = (sheep_data[sheep_id] >= abnormal_temp_thresh) & (sheep_data['date'] == current_date)
                tmp_data = sheep_data[condition][['DT', sheep_id]].copy()

                if tmp_data.shape[0] < 280:
                    print(f"⚠️ Insufficient data points (< 280) for {sheep_id} on {current_date}. Skipping.")
                    continue

                tmp_data['seconds'] = (tmp_data['DT'].dt.hour * 3600 +
                                        tmp_data['DT'].dt.minute * 60 +
                                        tmp_data['DT'].dt.second)
                tmp_data['time_hours'] = tmp_data['seconds'] / 3600

                tmp_data['Datetime'] = tmp_data['DT']
                tmp_data = tmp_data.set_index('Datetime')
                tmp_data = remove_outliers_interpolate_drink(tmp_data.copy(), sheep_id, abnormal_temp_thresh, temp_thresh)

                M, A, phi, r_squared = perform_cosinor_analysis(tmp_data[sheep_id].dropna(), tmp_data['time_hours'])

                cosinor_record = {
                    "group": sheep_id[0],
                    "sheep_id": sheep_id,
                    "record_date": current_date,
                    "record_num": tmp_data.shape[0],
                    "M": M,
                    "A": A,
                    "phi": phi,
                    "r_squared": r_squared,
                }

                if extract_min_max_temp:
                    for percent in percent_list:
                        min_val, max_val = extract_pointed_temp_value(tmp_data[sheep_id].dropna(), percent / 100.0)
                        cosinor_record[f'percent_{percent}_min'] = min_val
                        cosinor_record[f'percent_{percent}_max'] = max_val

                all_cosinor_data.append(cosinor_record)

                log_message = (
                    f"✅ {datetime.now().strftime('%H:%M:%S')} Processed: {sheep_id} | Date: {current_date}\n"
                    f"  M: {M:.2f}, A: {A:.2f}, φ: {phi:.2f}, R²: {r_squared:.2f}\n"
                )
                print(log_message)

            except Exception as e:
                print(f"⚠️ {datetime.now().strftime('%H:%M:%S')} Error processing {sheep_id} | Date: {current_date}: {e}\n")
                continue

        if all_cosinor_data:
            cosinor_df = pd.DataFrame(all_cosinor_data)
            output_file = os.path.join(OUTPUT_DIR, f'{sheep_id}_cosinor_features.csv')
            cosinor_df.to_csv(output_file, index=False)
            print(f"✅ Saved cosinor features for {sheep_id} to {output_file}")
        else:
            print(f"⚠️ No valid cosinor features extracted for {sheep_id}.")

    except Exception as e:
        print(f"⚠️ Error processing sheep {sheep_id} from {file_path}: {e}")


def process_single_sheep_drinking(file_path, sheep_id, abnormal_temp_thresh=35, temp_thresh=-0.5, extract_min_max_temp=True):
    """
    Process data for a single sheep from a CSV file.
    """
    try:
        sheep_data = pd.read_csv(file_path)
        if 'DT' not in sheep_data.columns or sheep_id not in sheep_data.columns:
            print(f"⚠️ Missing 'DT' or '{sheep_id}' column in {file_path}. Skipping.")
            return

        sheep_data['DT'] = pd.to_datetime(sheep_data['DT'])
        sheep_data['date'] = sheep_data['DT'].dt.date
        sheep_data['date'] = sheep_data['date'].astype('str')
        sheep_data['hour'] = sheep_data['DT'].dt.hour
        sheep_data['hour'] = sheep_data['hour'].astype('str')
        sheep_data['DataTime'] = sheep_data['DT']
        sheep_data.set_index('DataTime', inplace=True)

        drink_data_list = []
        sheep_record_date_list = sorted(sheep_data['date'].unique())

        for current_date in sheep_record_date_list:
            try:
                condition = (sheep_data[sheep_id] >= abnormal_temp_thresh) & (sheep_data['date'] == current_date)
                tmp_data = sheep_data[condition][['DT', sheep_id]].copy()

                if tmp_data.shape[0] < 280:
                    print(f"⚠️ Insufficient data points (< 280) for {sheep_id} on {current_date}. Skipping.")
                    continue

                # Filter abnormal values and using the interpolate method to makeup the data
                tmp_data['Datetime'] = tmp_data['DT']
                tmp_data = tmp_data.set_index('Datetime')

                selected_drink_data = drink_detection(tmp_data, sheep_id, temp_thresh=temp_thresh)

                if selected_drink_data.shape[0] == 0:
                    continue
                else:
                    selected_drink_data['hour'] = selected_drink_data['DT'].dt.hour
                    drink_data_list.append(selected_drink_data)

                log_message = f"✅ {datetime.now().strftime('%H:%M:%S')} Extracted: {sheep_id} | Date: {current_date}\n" \
                              f"   Drink count: {selected_drink_data.shape[0]}\n"
                print(log_message)

            except Exception as e:
                print(f"⚠️ {datetime.now().strftime('%H:%M:%S')} Error processing {sheep_id} | Date: {current_date}: {e}\n")
                continue

        if drink_data_list:
            drink_df = pd.concat(drink_data_list)
            output_file = os.path.join(OUTPUT_DRINK_DIR, f'{sheep_id}_drinking_behavior.csv')
            drink_df.to_csv(output_file, index=False)
            print(f"✅ Saved cosinor features for {sheep_id} to {output_file}")
        else:
            print(f"⚠️ No valid cosinor features extracted for {sheep_id}.")

    except Exception as e:
        print(f"⚠️ Error processing sheep {sheep_id} from {file_path}: {e}")

def split_data_by_sheep(input_excel_path, sheet_name='Sheet1'):
    """
    Loads the Excel file and splits the data into individual CSV files for each sheep.
    """
    try:
        sheep_data_all = pd.read_excel(input_excel_path, sheet_name=sheet_name)
        sheep_data_colums = [col for col in sheep_data_all.columns if 'DT' not in col and 'hour' not in col and 'date' not in col]

        for sheep_id in sheep_data_colums:
            sheep_df = sheep_data_all[['DT', sheep_id]].copy()
            output_csv_path = os.path.join(SPLITTED_DATA_DIR, f'{sheep_id}.csv')
            sheep_df.to_csv(output_csv_path, index=False)
            print(f"✅ Created splitted file for {sheep_id}: {output_csv_path}")

        return sheep_data_colums

    except FileNotFoundError:
        print(f"⚠️ Error: Excel file not found at {input_excel_path}")
        return []
    except Exception as e:
        print(f"⚠️ Error during data splitting: {e}")
        return []

def process_all_splitted_data(splitted_data_dir=SPLITTED_DATA_DIR, abnormal_temp_thresh=35, temp_thresh=-0.5, extract_min_max_temp=True):
    """
    Processes all the splitted CSV files in the specified directory.
    """
    splitted_files = [f for f in os.listdir(splitted_data_dir) if f.endswith('.csv')]
    for file_name in splitted_files:
        if file_name.endswith('.csv'):
            sheep_id = file_name.replace('.csv', '')
            file_path = os.path.join(splitted_data_dir, file_name)
            print(f"\n--- Processing sheep: {sheep_id} from {file_path} ---")
            process_single_sheep_cosinor(file_path, sheep_id, abnormal_temp_thresh, temp_thresh, extract_min_max_temp)
            process_single_sheep_drinking(file_path, sheep_id, abnormal_temp_thresh, temp_thresh, extract_min_max_temp)

if __name__ == "__main__":
    #  Assume your large Excel file is named 'rumen_temp_large.xlsx'. (假设你的大 Excel 文件名为 'rumen_temp_large.xlsx')
    large_excel_file = "C:/Users/22828187/Desktop/Excel File BK/newest_data/AAA 2024 KELLERBERRIN CALIBRATED.xlsx"
    sheet_name = 'CALIB'
    abnormal_temp_thresh = 35
    temp_thresh = -0.8
    extract_min_max_temp = True

    # 1. Split data (拆分数据)
    sheep_ids = split_data_by_sheep(large_excel_file, sheet_name)

    if sheep_ids:
        print("\n--- Starting single-threaded processing of each sheep ---")
        # 2. Process split data in a single thread (单线程处理拆分后的数据)
        process_all_splitted_data(SPLITTED_DATA_DIR, abnormal_temp_thresh, temp_thresh, extract_min_max_temp)
        print("\n✅ Finished processing all sheep data.")
    else:
        print("⚠️ No sheep data found or splitting failed.")