import csv
import json
import os.path
import collections
import datetime


def read_csv_file(filename: str) -> list:
    """
    Reads financial data from a CSV file and converts it to a standard format.

    Args:
        filename (str):  The path to the CSV file

    Returns:
        list: A list of dictionaries with transactions in a unified format
    """

    data = []

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            read_csv = csv.DictReader(file)

            for row in read_csv:
                amount = float(row.get('amount', 0))
                transact_type = "доход" if amount >= 0 else "расход"

                transaction = {
                    'date': row.get('date', '').strip(),
                    'amount': amount,
                    'description': row.get('description', '').strip(),
                    'type': transact_type
                }
                data.append(transaction)

            return data

    except FileNotFoundError:
        print("Error: The CSV file could not be found.")
        return []


def read_json_file(filename: str) -> list:
    """
    Reads financial data from a JSON file and converts it to a standard format.

    Args:
        filename (str):  The path to the JSON file

    Returns:
        list: A list of dictionaries with transactions in a unified format
    """

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            read_json = json.load(file)

            transactions = read_json.get('transactions', [])
            single_format = []

            for operation in transactions:
                amount = float(operation.get('amount', 0))
                transact_type = "доход" if amount >= 0 else "расход"

                transaction = {
                    'date': operation.get('date', '').strip(),
                    'amount': amount,
                    'description': operation.get('description', '').strip(),
                    'type': transact_type
                }
                single_format.append(transaction)

            return single_format

    except FileNotFoundError:
        print("Error: The JSON file could not be found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file")
        return []



def import_financial_data(filename: str):
    """
    Automatically detects the file format by extension and calls
    the appropriate function.

    Args:
        filename (str):  The path to the file (CSV or JSON)

    Returns:
        list: A list of dictionaries with transactions in a unified format
    """

    if not os.path.exists(filename):
        print(f"Error: File does not exist.")
        return []

    file_type = os.path.splitext(filename)[1].lower()

    if file_type == '.csv':
        result = read_csv_file(filename)
    elif file_type == '.json':
        result = read_json_file(filename)
    else:
        print(f"Error: Unsupported file format")
        return []
    return result


def categorize_transaction_with_multiple(description: str, categories: dict,
                                         categories_priority: list) -> str:

    description_low = description.lower()
    matched_categories = []

    for category in categories_priority:
        keywords = categories.get(category, [])
        if any(keyword in description_low for keyword in keywords):
            matched_categories.append(category)

    if matched_categories:
        return matched_categories[0]
    return "другое"


def categorize_all_transactions(transactions: list) -> list:

    for transaction in transactions:
        desc = transaction.get("description", "")
        category = categorize_transaction_with_multiple(desc, categories, categories_priority)
        transaction["category"] = category
    return transactions


#шаг 1 : Посчитать основные показатели
def calculate_basic_stats(transactions: list) -> dict:
    total_income = sum(t['amount'] for t in transactions
                       if t['amount'] > 0)
    total_expense = sum(t['amount'] for t in transactions
                        if t['amount'] < 0)
    balance = total_income + total_expense
    count_transactions = len(transactions)#испольховала sum() и len() для подсчетов
    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'transaction_count': count_transactions
    }

#Шаг 2: Разложить по категориям
def calculate_by_category(transactions: list) -> dict: # transactions — список словарей
    category_totals = {}#словарь для группировки (см технические подсказки)
    total_expenses = sum(t['amount'] for t in transactions
                         if t['amount'] < 0)

    for t in transactions:
        category = t.get('category', 'Без категории') #пытаемся извлечь название категории по ключу 'category', иначе
        if category not in category_totals:
            category_totals[category] = {'sum': 0, 'count': 0}
        category_totals[category]['sum'] += t['amount']
        category_totals[category]['count'] += 1

    # Вычисляем процент от общих расходов
    for cat, data in category_totals.items():
        data['percent'] = (-data['sum'] / -total_expenses * 100) if total_expenses != 0 else 0

    return category_totals


# Функция для анализа по времени (по месяцам)
def analyze_by_time(transactions: list) -> dict:
    monthly_stats = {}

    for t in transactions:
        date_obj = datetime.datetime.strptime(t['date'], '%Y-%m-%d')
        month_key = date_obj.strftime('%Y-%m')  # например, '2024-01'
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {
                'income': 0,
                'expenses': 0,
                'categories': []
            }
        if t['amount'] > 0:
            monthly_stats[month_key]['income'] += t['amount']
        elif t['amount'] < 0:
            monthly_stats[month_key]['expenses'] += t['amount']
            monthly_stats[month_key]['categories'].append(t.get('category', 'Без категории'))

    # Анализ самых частых категорий за месяц
    for month, data in monthly_stats.items():
        category_counter = collections.Counter(data['categories'])
        most_common = category_counter.most_common(3)
        data['top_categories'] = most_common

    return monthly_stats


# Пример использования
def main():
    print("=" * 60)
    print("ФИНАНСОВЫЙ АНАЛИЗАТОР")
    print("=" * 60)

    print("ИМПОРТ ДАННЫХ ИЗ ФАЙЛОВ")
    print("-" * 40)

    data_csv = import_financial_data('money.csv')
    data_json = import_financial_data('transactions.json')

    if not data_csv and not data_json:
        print("Нет данных для анализа. Проверьте наличие файлов.")
        return

    all_transactions = data_csv + data_json

    transactions = categorize_all_transactions(all_transactions)

    # Расчет основных показателей
    print("Основные показатели:")
    print("-" * 40)
    basic_stats = calculate_basic_stats(transactions)
    print(f"💰 Доходы: {basic_stats['total_income']:.2f} руб.")#округление числа до 2 х знаков после запятой
    print(f"💸 Расходы: {abs(basic_stats['total_expense']):.2f} руб.")
    print(f"⚖️ Баланс: {basic_stats['balance']:.2f} руб.")

    # Расчет по категориям
    category_stats = calculate_by_category(transactions)
    print("\nРасходы по категориям:")
    for category, data in category_stats.items():
        print(f"{category}: {abs(data['sum']):.2f} руб. ({data['percent']:.1f}%)")

    # Анализ по времени
    timeline = analyze_by_time(transactions)
    print("\nАнализ по месяцам:")
    for month, data in timeline.items():
        print(f"\nМесяц: {month}")
        print(f" Доходы: {data['income']:.2f} руб.")
        print(f" Расходы: {abs(data['expenses']):.2f} руб.")
        print("Топ категорий расхода:")
        for cat, count in data['top_categories']:
            print(f"  {cat}: {count} транзакций")

categories = {
    "продукты": ["продукты", "магазин", "продуктовый", "пятёрочка", "ника", "касира"],
    "обед и рестораны": ["ресторан", "кафе", "обед", "бесплатно", "ужин", "завтрак"],
    "транспорт": ["такси", "автобус", "метро", "транспорт", "билет"],
    "услуги": ["мобильный", "интернет", "услуга", "сервис", "ремонт"],
    "развлечения": ["кино", "театр", "концерт", "игры", "кинотеатр"],
    "одежда": ["одежда", "обувь", "магазин одежды", "гардероб"],
    "здравоохранение": ["аптека", "лекарство", "медицин", "врач"],
    "спорт": ["спорт", "тренажёрка", "фитнес", "спортзал"],
    "образование": ["курс", "учеба", "школа", "университет"],
    "коммунальные услуги": ["Коммуналка", "вода", "электричество", "газ"],
    "депозит/инвестиции": ["клиентов", "депозит", "инвестиции"],
    "зарплата и доходы": ["зарплата", "доход", "перевод"],
    "погашение кредита": ["кредит", "ипотека", "погашение"],
    "подарки": ["подарок", "поздравление"],
    "налоги": ["налог", "фискальный"]
    }

categories_priority = [
    "зарплата и доходы",
    "погашение кредита",
    "продукты",
    "обед и рестораны",
    "транспорт",
    "услуги",
    "развлечения",
    "одежда",
    "здравоохранение",
    "спорт",
    "образование",
    "коммунальные услуги",
    "депозит/инвестиции",
    "подарки",
    "налоги"
    ]

if __name__ == "__main__":
    main()
