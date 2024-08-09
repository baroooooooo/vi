import pandas as pd
import json

COLUMNS = ['actor', 'timeStamp', 'object', 'result', 'verb', 'extension']

def verb_change(data_list):
    VERB_COLUMN = 'verb'
    delete_line = []
    
    for i, record in enumerate(data_list):
        
        if not isinstance(record, dict):
            print(f"Skipping record {i}: not a dictionary")
            delete_line.append(i)
            continue
        
        if 'timeStamp' not in record:
            print(f"Skipping record {i}: 'timeStamp' not in record")
            delete_line.append(i)
            continue
        
        try:
            verb_content = record[VERB_COLUMN]
            if verb_content.startswith('{') or verb_content.startswith('['):
                verb_data = json.loads(verb_content)
                if isinstance(verb_data, list) and len(verb_data) > 0 and 'display' in verb_data[0]:
                    display_value = verb_data[0]['display']
                else:
                    delete_line.append(i)
                    continue
            else:
                display_value = verb_content
            
            if display_value.startswith('launched') or display_value.startswith('started'):
                record[VERB_COLUMN] = 1
            elif display_value.startswith('finished') or display_value.startswith('moved'):
                record[VERB_COLUMN] = 0
            elif display_value.startswith('suspended') or display_value.startswith('completed'):
                record[VERB_COLUMN] = -1
            else:
                delete_line.append(i)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError for record {i}: {e}")
            delete_line.append(i)
        except (KeyError, IndexError) as e:
            print(f"Error processing record {i}: {e}")
            delete_line.append(i)
    
    for d in sorted(delete_line, reverse=True):
        data_list.pop(d)
    
    return data_list

def stamp_to_deff_time(df):
    if 'timeStamp' not in df.columns:
        raise KeyError("'timeStamp' column not found in the data")
    try:
        df['timeStamp'] = pd.to_datetime(df['timeStamp'], utc=True)
    except Exception:
        raise ValueError("Error parsing 'timeStamp' column")
    df = df.sort_values('timeStamp')
    df['time_diff'] = df['timeStamp'].diff().dt.total_seconds()
    return df

def to_value_list(data):
    if len(data[0]) != len(COLUMNS):
        raise Exception('Invalid columns length')
    seikei_list = []
    for row in data:
        row_dict = dict(zip(COLUMNS, row))
        seikei_list.append(row_dict)
    return seikei_list
