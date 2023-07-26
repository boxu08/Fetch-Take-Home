"""
Script Name: search_offers.py
Author: Bo Xu
Date: July 26, 2023

Description:
This script defines functions used for searching offers.
"""
import pandas as pd
from utils import phrase_similarity


def prepare_expanded_category_table(categories_df: pd.DataFrame):
    """
    This function prepars the expanded category table.
    The expanded category table is the categories table expanded vertically by creating multiple
    rows in the case that a category is a conjunction of multiple categories. For example, "Nuts & Seeds"
    is split into two rows, one as "Nuts" and the other as "Seeds". Furthermore, the parent category (i.e.,
    IS_CHILD_CATEGORY_TO) is treated as a category (or multiple categories if it's a conjunction) as well. The
    parent category of "Nuts & Seeds" is "Snacks". Thus, "Nuts & Seeds" will be expanded to three rows in the
    expanded table, with the value for the "CATEGORY" attribute being "Nuts", "Seeds", and "Snacks", respectively.


    Args:
        categories_df (pd.DataFrame): the original category table.

    Returns:
        pd.DataFrame: The expanded category table.
    """
    expanded_category_df = pd.DataFrame(columns = ['CATEGORY_ID', 'CATEGORY'])
    for _, row in categories_df.iterrows():
        category_id = row['CATEGORY_ID']

        # expand based on PRODUCT_CATEGORY
        product_category = row['PRODUCT_CATEGORY']
        # split by , and & since they represent conjunction
        expanded_categories = product_category.replace(',', '&').split('&')
        for category in expanded_categories:
            expanded_category_df.loc[len(expanded_category_df)] = [category_id, category]

        # expand based on parent category (i.e., IS_CHILD_CATEGORY_TO)
        parent_category = row['IS_CHILD_CATEGORY_TO']
        # split by , and &
        expanded_categories = parent_category.replace(',', '&').split('&')
        for category in expanded_categories:
            expanded_category_df.loc[len(expanded_category_df)] = [category_id, category]

    return expanded_category_df


def prepare_offer_category_table(offer_retailer_df: pd.DataFrame, brand_category_df: pd.DataFrame, categories_df: pd.DataFrame):
    """
    This function joins the three original tables to get a table where each row represents an association between
    an offer and its category. This table will be used for category based search.


    Args:
        offer_retailer_df (pd.DataFrame): the original offer_retailer table.
        brand_category_df (pd.DataFrame): the original brand_category table.
        categories_df (pd.DataFrame): the original category table.

    Returns:
        pd.DataFrame: The joined table.
    """

    # Assign each offer with a unique offer id.
    offer_retailer_df_with_offer_id = offer_retailer_df.reset_index().rename(columns={'index': 'OFFER_ID'})

    # Join the three original tables
    offer_category_df = offer_retailer_df_with_offer_id.merge(brand_category_df, on='BRAND', how='left')
    offer_category_df = offer_category_df.rename(columns={'BRAND_BELONGS_TO_CATEGORY': 'PRODUCT_CATEGORY'})
    offer_category_df = offer_category_df.merge(categories_df, on='PRODUCT_CATEGORY', how='left')

    return offer_category_df


# brand search
def brand_search(input_brand, offer_retailer_df, min_score=0.5):
    """
    This function searches offers based on brand.


    Args:
        input_brand (str): the input brand string.
        offer_retailer_df (pd.DataFrame): the original offer_retailer table.
        min_score (float): only the offers with brand matching score higher than or equal to min_score will be returned.

    Returns:
        pd.DataFrame: The searched offers.
    """
    offer_retailer_scored_df = offer_retailer_df.copy()
    offer_retailer_scored_df['BRAND_SCORE'] = offer_retailer_scored_df['BRAND'].apply(phrase_similarity,
                                                                                      args=(input_brand,))
    offer_retailer_scored_df = offer_retailer_scored_df[offer_retailer_scored_df['BRAND_SCORE'] >= min_score]
    offer_retailer_scored_df = offer_retailer_scored_df.sort_values('BRAND_SCORE', ascending=False)
    return offer_retailer_scored_df


# retailer search
def retailer_search(input_retailer, offer_retailer_df, min_score=0.5):
    """
    This function searches offers based on retailer.


    Args:
        input_retailer (str): the input retailer string.
        offer_retailer_df (pd.DataFrame): the original offer_retailer table.
        min_score (float): only the offers with retailer matching score higher than or equal to min_score
                           will be returned.

    Returns:
        pd.DataFrame: The searched offers.
    """
    offer_retailer_scored_df = offer_retailer_df.copy()
    offer_retailer_scored_df['RETAILER_SCORE'] = offer_retailer_scored_df['RETAILER'].apply(phrase_similarity,
                                                                                            args=(input_retailer,))
    offer_retailer_scored_df = offer_retailer_scored_df[offer_retailer_scored_df['RETAILER_SCORE'] >= min_score]
    offer_retailer_scored_df = offer_retailer_scored_df.sort_values('RETAILER_SCORE', ascending=False)
    return offer_retailer_scored_df


# category search
def category_search(input_category, expanded_category_df, offer_category_df, min_score=0.5):
    """
    This function searches offers based on category. In the case that an offer is associated with multiple categories,
    the highest category matching score is taken to be the offer's category matching score.


    Args:
        input_category (str): the input retailer string.
        expanded_category_df (pd.DataFrame): the expanded category table (see prepare_expanded_category_table).
        offer_category_df (pd.DataFrame): the joined table (see prepare_offer_category_table).
        min_score (float): only the offers with category matching score higher than or equal to min_score
                           will be returned.

    Returns:
        pd.DataFrame: The searched offers.
    """

    category_score_df = expanded_category_df.copy()
    # compute matching score for each expanded category entry
    category_score_df['SCORE'] = category_score_df['CATEGORY'].apply(phrase_similarity, args=(input_category,))

    # keep the highest score as the final score of each category_id
    category_final_score = pd.DataFrame(columns=['CATEGORY_ID', 'CATEGORY_SCORE'])
    by_category_id = category_score_df.groupby('CATEGORY_ID')
    for category_id, group in by_category_id:
        final_score = group['SCORE'].max()
        category_final_score.loc[len(category_final_score)] = [category_id, final_score]

    # now we associate each offer and its each category with a final score
    offer_category_scored_df = offer_category_df.merge(category_final_score, on='CATEGORY_ID', how='left')

    # since an offer may be associated with multiple categories, we take the highest score
    offer_category_scored_df = offer_category_scored_df.dropna(subset=['CATEGORY_SCORE'])
    by_offer_id = offer_category_scored_df.groupby('OFFER_ID')
    idxs = []
    for offer_id, group in by_offer_id:
        idxs.append(group['CATEGORY_SCORE'].idxmax())
    offer_category_scored_df = offer_category_scored_df.loc[idxs]

    # now we select the offers with category matching score higher than the threshold
    offer_category_scored_df = offer_category_scored_df[offer_category_scored_df['CATEGORY_SCORE'] >= min_score]
    offer_category_scored_df = offer_category_scored_df.sort_values('CATEGORY_SCORE', ascending=False)

    # for a user to see why an offer is selected, we display 'PRODUCT_CATEGORY' and 'IS_CHILD_CATEGORY_TO'
    offer_category_scored_df = offer_category_scored_df[
        ['OFFER', 'RETAILER', 'BRAND', 'PRODUCT_CATEGORY', 'IS_CHILD_CATEGORY_TO', 'CATEGORY_SCORE']]

    return offer_category_scored_df
