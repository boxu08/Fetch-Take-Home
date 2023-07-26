# Introduction
This repository contains my submission to Fetch's Data Science Take Home challenge.  

# Instructions for Running (tested on python 3.8 and 3.11)
1. Install Python packages pandas, nltk, tabulate, pyyaml if you have not done so yet.
2. Go to src directory.
3. python main.py
4. Follow the displayed instructions to use the search tool.

# Design Ideas
## Phrase Matching
Given an input phrase, I take the following steps to calculate a matching (similarity) score between this 
phrase and a target phrase associated with an offer (i.e., category, brand, or retailer):

1. Remove punctuations from the input phrase and the target phrase.
2. Remove stop words from the input phrase and the target phrase. It is unlikely that stop words appear
in the context of our application but I remove them anyways.
3. Stem each word (so that "beverage" will match "beverages" for example).
4. Tokenize the input phrase and the target phrase respectively.
5. Compute the Jaccard similarity between the input tokens and the target tokens.

## Searching Offers based on Categories
Searching offers based on categories introduces the following two special challenges:

1. Each product category is associated with a parent category (i.e., IS_CHILD_CATEGORY_TO). How to
consolidate the matching score for a category and that for its parent category?
2. A category may be a conjunction of multiple categories. For example, "Nuts & Seeds"
should perfectly match a search category of "Nuts". However, if we preprocess category phrases
in a usual way by removing punctuations, "Nuts & Seeds" will become "Nuts Seeds", and "Nuts" will only
have a partial match.

To deal with the above two issues, I expand the original category table vertically by creating multiple
    rows for each *conjunctive category*. A conjunctive category is a category that contains "," or "&".
For example, "Nuts & Seeds" is a conjunctive category, so is "Cereal, Granola, & Toaster Pastries".
    I split each conjunctive category by "," and "&" to multiple categories that I call *derived categories*. 
For example, "Nuts & Seeds" is split into "Nuts" and "Seeds", and "Cereal, Granola, & Toaster Pastries"
is split into "Cereal", "Granola", "Toaster Pastries". Furthermore, the parent category
    is treated as a derived category (or multiple derived categories if it is conjunctive) as well. The
    parent category of "Nuts & Seeds" is "Snacks". Thus, "Nuts & Seeds" will eventually be expanded to three rows in the
    expanded table, with the value for the "CATEGORY" attribute being "Nuts", "Seeds", and "Snacks", respectively.

Once I generate derived categories for each original category, the matching score of that original
category is equal to the highest matching score of all its derived categories.
Therefore, whether a user asks for "Nuts", or "Seeds", or "Snacks", an offer with category being "Nuts & Seeds" will
get a perfect matching score, which is what we want.
