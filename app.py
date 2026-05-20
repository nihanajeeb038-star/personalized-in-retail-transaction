from flask import Flask, render_template, request
import pickle
import pandas as pd
import webbrowser

app = Flask(__name__)

# AUTO RELOAD + NO CACHE
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# LOAD FILES
products = pickle.load(open('products.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# PRODUCT LIST
product_list = products['Product Name'].drop_duplicates().values

# FILTER DATA
categories = products['Category'].drop_duplicates().values
colors = products['Color'].drop_duplicates().values

# SEARCH HISTORY
search_history = []

# TRENDING PRODUCTS
trending_products = (
    products[['Product Name', 'Category']]
    .drop_duplicates(subset='Product Name')
    .head(6)
    .to_dict(orient='records')
)

# RECOMMEND FUNCTION
def recommend(product_name, category, color):

    recommended_products = []

    filtered_products = products.copy()

    # CATEGORY FILTER
    if category != "All":

        filtered_products = filtered_products[
            filtered_products['Category'] == category
        ]

    # COLOR FILTER
    if color != "All":

        filtered_products = filtered_products[
            filtered_products['Color'].str.strip().str.lower()
            == color.strip().lower()
        ]

    # PRODUCT SIMILARITY
    if product_name:

        try:

            index = products[
                products['Product Name'] == product_name
            ].index[0]

            distances = similarity[index]

            product_list_sorted = sorted(
                list(enumerate(distances)),
                reverse=True,
                key=lambda x: x[1]
            )[1:50]

            matched_products = []

            for i in product_list_sorted:

                product_index = i[0]

                product = products.iloc[product_index]

                # CATEGORY CHECK
                if category != "All":
                    if product['Category'] != category:
                        continue

                # COLOR CHECK
                if color != "All":
                    if (
                        str(product['Color']).strip().lower()
                        != color.strip().lower()
                    ):
                        continue

                matched_products.append(product)

            # ONLY REPLACE IF MATCH EXISTS
            if matched_products:

                filtered_products = pd.DataFrame(matched_products)

        except:
            pass

    # REMOVE DUPLICATES
    filtered_products = filtered_products.drop_duplicates(
        subset='Product Name'
    )

    # SORT BY SIMILARITY DESCENDING
    if product_name:

        try:

            selected_index = products[
                products['Product Name'] == product_name
            ].index[0]

            filtered_products['similarity_score'] = (
                filtered_products['Product Name']
                .apply(
                    lambda x: similarity[selected_index][
                        products[
                            products['Product Name'] == x
                        ].index[0]
                    ]
                )
            )

            filtered_products = filtered_products.sort_values(
                by='similarity_score',
                ascending=False
            )

        except:
            pass

    # FINAL OUTPUT
    if not filtered_products.empty:

        for _, row in filtered_products.iterrows():

            similarity_score = "Recommended"

            if product_name:

                try:

                    original_index = products[
                        products['Product Name']
                        == row['Product Name']
                    ].index[0]

                    selected_index = products[
                        products['Product Name']
                        == product_name
                    ].index[0]

                    similarity_score = str(
                        round(
                            similarity[selected_index][original_index]
                            * 100,
                            2
                        )
                    ) + '%'

                except:
                    similarity_score = "Recommended"

            recommended_products.append({
                'name': row['Product Name'],
                'category': row['Category'],
                'similarity': similarity_score
            })

    else:

        recommended_products.append({
            'name': 'No Products Available',
            'category': 'Not Available',
            'similarity': '0%'
        })

    return recommended_products


# HOME PAGE
@app.route('/', methods=['GET', 'POST'])
def index():

    recommendations = []

    selected_product = None

    global search_history

    if request.method == 'POST':

        selected_product = request.form.get('product')

        selected_category = request.form.get('category')

        selected_color = request.form.get('color')

        recommendations = recommend(
            selected_product,
            selected_category,
            selected_color
        )

        # SAVE SEARCH HISTORY
        if selected_product and selected_product not in search_history:

            search_history.insert(0, selected_product)

        # KEEP ONLY LAST 5
        search_history = search_history[:5]

    return render_template(
        'index.html',
        products=product_list,
        recommendations=recommendations,
        selected_product=selected_product,
        search_history=search_history,
        trending_products=trending_products,
        categories=categories,
        colors=colors
    )


# RUN APP
if __name__ == '__main__':

    webbrowser.open('http://127.0.0.1:5000')

    app.run(debug=True, use_reloader=True)