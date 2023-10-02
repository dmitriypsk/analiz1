import pandas as pd
import matplotlib.pyplot as plt

# Path to the data file
file_path = "/Users/dmitriy/Downloads/Презентация/Д•в†Ђ®І†ж®п І†ђ•аЃҐ І† 1 ™Ґ†ав†Ђ.txt"

# Read the file with UTF-16 
try:
    data = []
    with open(file_path, 'r', encoding='utf-16') as file:
        for line in file:
            line = line.strip()
            if line:
                data.append(dict(item.split('=') for item in line.split('|')))
except FileNotFoundError:
    print("Файл не найден. Пожалуйста, проверьте путь к файлу.")
    exit(1)
except Exception as e:
    print(f"Произошла ошибка при чтении файла: {e}")
    exit(1)

# Check if data is empty
if not data:
    print("Файл пуст или данные не распознаны.")
    exit(1)

# Convert to DataFrame and handle missing or erroneous data
df = pd.DataFrame(data)
df['raiting'] = pd.to_numeric(df['raiting'], errors='coerce')
df.dropna(subset=['raiting'], inplace=True)

# Aggregate data
total_calls = len(df)
satisfied_calls = len(df[df['raiting'] >= 4])
dissatisfied_calls = len(df[df['raiting'] == 1])
unaccounted_calls = total_calls - satisfied_calls - dissatisfied_calls

# Calculate CSI and CDI
CSI = (satisfied_calls / total_calls) * 100
CDI = (dissatisfied_calls / total_calls) * 100

# Visualization
labels = ['CSI', 'CDI']
values = [CSI, CDI]

plt.figure(figsize=(8, 5))
bars = plt.bar(labels, values, color=['green', 'red'])

# Annotation
for bar in bars:
    plt.text(bar.get_x() + bar.get_width() / 2 - 0.1, bar.get_height() - 5, f'{bar.get_height():.2f}%')

# Labels and title
plt.xlabel('Индексы')
plt.ylabel('Процент (%)')
plt.title('Уровень удовлетворённости и неудовлетворённости клиентов за квартал')
plt.ylim(0, 105)
plt.grid(axis='y')

plt.show()

# Textual Summary
text_summary = f"""
Выводы на основе данных за квартал:

Выводы на основе данных за квартал:

1. Общее количество звонков: {total_calls}
2. Количество неучтенных звонков: {unaccounted_calls}
3. CSI (Customer Satisfaction Index): {CSI:.2f}%
4. CDI (Customer Dissatisfaction Index): {CDI:.2f}%

"""
print(text_summary)

# Группировка данных по 'call_start_dt' и расчет CSI и CDI
df_grouped = df.groupby('call_start_dt').apply(lambda x: pd.Series({
    'total_calls': len(x),
    'satisfied_calls': len(x[x['raiting'] >= 4]),
    'dissatisfied_calls': len(x[x['raiting'] == 1]),
}))

df_grouped['CSI'] = (df_grouped['satisfied_calls'] / df_grouped['total_calls']) * 100
df_grouped['CDI'] = (df_grouped['dissatisfied_calls'] / df_grouped['total_calls']) * 100

# Визуализация
plt.figure(figsize=(12, 6))
plt.plot(df_grouped.index, df_grouped['CSI'], label='CSI', color='green')
plt.plot(df_grouped.index, df_grouped['CDI'], label='CDI', color='red')
plt.xlabel('call_start_dt')
plt.ylabel('Процент (%)')
plt.title('Динамика уровня удовлетворённости и неудовлетворённости клиентов')
plt.legend()
plt.grid(True)
plt.show()

# Конвертируем столбцы в числовые значения
for column in ['ivr_talk_sec', 'oper_wait_sec', 'oper_talk_sec']:
    df[column] = pd.to_numeric(df[column], errors='coerce')

# Функция для расчета CSI и CDI
def calculate_csi_cdi(group):
    total_calls = len(group)
    satisfied_calls = len(group[group['raiting'] >= 4])
    dissatisfied_calls = len(group[group['raiting'] == 1])
    uncounted_calls = total_calls - satisfied_calls - dissatisfied_calls  
    CSI = (satisfied_calls / total_calls) * 100 if total_calls > 0 else 0
    CDI = (dissatisfied_calls / total_calls) * 100 if total_calls > 0 else 0
    return pd.Series({'CSI': CSI, 'CDI': CDI, 'Uncounted': uncounted_calls}) 


# Анализируем по каждому показателю
for column in ['ivr_talk_sec', 'oper_wait_sec', 'oper_talk_sec']:
    # Группируем данные по бинам (можно использовать любой размер бина)
    df[column+'_bin'] = pd.cut(df[column], bins=range(0, int(df[column].max()) + 50, 50))
    grouped_data = df.groupby(column+'_bin').apply(calculate_csi_cdi)

   

# Визуализация
for column in ['ivr_talk_sec', 'oper_wait_sec', 'oper_talk_sec']:
    df[column+'_bin'] = pd.cut(df[column], bins=range(0, int(df[column].max()) + 50, 50))
    grouped_data = df.groupby(column+'_bin').apply(calculate_csi_cdi)

    plt.figure(figsize=(12, 6))
    plt.plot(grouped_data.index.astype(str), grouped_data['CSI'], label='CSI', color='green')
    plt.plot(grouped_data.index.astype(str), grouped_data['CDI'], label='CDI', color='red')
    plt.plot(grouped_data.index.astype(str), grouped_data['Uncounted'], label='Uncounted', color='blue')  
    plt.xticks(rotation=45)
    plt.xlabel(column)
    plt.ylabel('Процент (%) или количество звонков')
    plt.title(f'Динамика CSI, CDI и неучтенных звонков по {column}')
    plt.legend()
    plt.grid(True)
    plt.show()


   

# Посмотреть на 3.85% недовольных клиентов
dissatisfied_data = df[df['raiting'] == 1]
dissatisfied_by_channel = dissatisfied_data['channel'].value_counts()
print(f"Распределение недовольных клиентов по каналам:\n{dissatisfied_by_channel}")

# Изучить 91.57% удовлетворенных клиентов
satisfied_data = df[df['raiting'] >= 4]
satisfied_by_channel = satisfied_data['channel'].value_counts()
print(f"\nРаспределение удовлетворенных клиентов по каналам:\n{satisfied_by_channel}")

# Сравнить CSI и CDI по каждому каналу
channel_data = df.groupby('channel').apply(calculate_csi_cdi)
print(f"\nСравнение CSI и CDI по каналам:\n{channel_data}")

# Неучтенные данные
uncounted_calls = total_calls - satisfied_calls - dissatisfied_calls
print(f"\nКоличество неучтенных звонков: {uncounted_calls}")

# Влияние временных показателей на уровень удовлетворенности
for column in ['ivr_talk_sec', 'oper_wait_sec', 'oper_talk_sec']:
    df_grouped_time = df.groupby(pd.cut(df[column], bins=range(0, int(df[column].max()) + 50, 50))).apply(calculate_csi_cdi)
    print(f"\nВлияние {column} на уровень удовлетворенности:\n{df_grouped_time}")

# Конвертируем 'client_age' в числовой формат
df['client_age'] = pd.to_numeric(df['client_age'], errors='coerce')

# Группировка данных по 'client_gender'
gender_grouped = df.groupby('client_gender').apply(calculate_csi_cdi)
print(f"CSI и CDI по полу клиента:\n{gender_grouped}")

# Группировка данных по 'client_age' (можно разбить на возрастные группы)
age_bins = [0, 18, 35, 50, 65, 100]
df['age_group'] = pd.cut(df['client_age'], bins=age_bins)
age_grouped = df.groupby('age_group').apply(calculate_csi_cdi)
print(f"CSI и CDI по возрастным группам:\n{age_grouped}")

# Визуализация для 'client_gender'
plt.figure(figsize=(8, 5))
plt.bar(gender_grouped.index, gender_grouped['CSI'], label='CSI', color='green')
plt.bar(gender_grouped.index, gender_grouped['CDI'], label='CDI', color='red')
plt.xlabel('Пол')
plt.ylabel('Процент (%)')
plt.title('Уровень удовлетворённости и неудовлетворённости по полу')
plt.legend()
plt.show()

# Визуализация для 'age_group'
plt.figure(figsize=(12, 6))
plt.bar(age_grouped.index.astype(str), age_grouped['CSI'], label='CSI', color='green')
plt.bar(age_grouped.index.astype(str), age_grouped['CDI'], label='CDI', color='red')
plt.xlabel('Возрастные группы')
plt.ylabel('Процент (%)')
plt.title('Уровень удовлетворённости и неудовлетворённости по возрастным группам')
plt.legend()
plt.show()


