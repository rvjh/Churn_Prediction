

def test_prepare_features():
    churn_input = {
        'customer_age': 100,
        'gender': 'F',
        'dependent_count': 2,
        'education_level': 2,
        'marital_status': 'married',
        'income_category': 2,
        'card_category': 'blue',
        'months_on_book': 6,
        'total_relationship_count': 3,
        'credit_limit': float(4000),
        'total_revolving_bal': 2500
    }
    expected_features = {
        'customer_age': 100,
        'gender': 'F',
        'dependent_count': 2,
        'education_level': 2,
        'marital_status': 'married',
        'income_category': 2,
        'card_category': 'blue',
        'months_on_book': 6,
        'total_relationship_count': 3,
        'credit_limit': float(4000),
        'total_revolving_bal': 2500
    }
    assert churn_input == expected_features

