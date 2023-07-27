"""
Script Name: main.py
Author: Bo Xu
Date: July 26, 2023

Description:
This script provides a simple CLI for a user to search offers based an input category, brand, or retailer
"""
from tabulate import tabulate
from search_offers import *
import yaml
import nltk


def get_min_score_from_yaml(file_path: str):
    """
    This function gets the min_score parameter from a file_path.
    The min_score parameter regulates that only the offers with matching score higher than
    min_score will be displayed.

    Args:
        file_path (str): The file path where min_score is stored.

    Returns:
        float: The min_score parameter
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)

    if 'min_score' in config:
        min_score = config['min_score']
    else:
        # Handle the case when 'min_category_score' is not found in the YAML file
        min_score = 0.5

    return min_score


if __name__ == '__main__':
    # get the min_score parameter
    min_score = get_min_score_from_yaml('../config/config.yaml')

    # load data files
    categories_df = pd.read_csv('../data/categories.csv')
    offer_retailer_df = pd.read_csv('../data/offer_retailer.csv')
    brand_category_df = pd.read_csv('../data/brand_category.csv')

    # download punkt for tokenization
    nltk.download('punkt')
    # download stopwords for stopwords removing
    nltk.download('stopwords')

    # prepare tables that will be used for category searching
    expanded_category_df = prepare_expanded_category_table(categories_df)
    offer_category_df = prepare_offer_category_table(offer_retailer_df, brand_category_df, categories_df)

    while True:
        # Display prompts
        print('\n\n')
        print("Please choose any of the following queries by typing in the number before the query:")
        print("1. Search offers relevant to a given category.")
        print("2. Search offers relevant to a given brand.")
        print("3. Search offers relevant to a given retailer.")
        print("0. Quit")

        query_choice = input("Your choice (1 or 2 or 3 or 0):")
        if query_choice not in ('1', '2', '3', '0'):
            print(query_choice, "is an invalid choice.\n\n")
            continue
        query_choice = int(query_choice)

        if query_choice == 1:
            input_category = input("Now input the category you want to search for (e.g., Coffee): ")
            result = category_search(input_category, expanded_category_df, offer_category_df, min_score)
            print(tabulate(result, headers='keys', tablefmt='psql', showindex=False))
        elif query_choice == 2:
            input_brand = input("Now input the brand you want to search for (e.g., SAMS): ")
            result = brand_search(input_brand, offer_retailer_df, min_score)
            print(tabulate(result, headers='keys', tablefmt='psql', showindex=False))
        elif query_choice == 3:
            input_brand = input("Now input the retailer you want to search for (e.g., AMAZON): ")
            result = retailer_search(input_brand, offer_retailer_df, min_score)
            print(tabulate(result, headers='keys', tablefmt='psql', showindex=False))
        elif query_choice == 0:
            quit()
