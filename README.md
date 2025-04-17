# AIFA - AI Foundry Analytics
![LOGO AIFA - BOITATÁ](assets/images/logos/logo1.png)

## Overview

AIFA (AI Foundry Analytics) is a project designed to assist users in deploying various Generative AI (GenAI) techniques for analytics tasks. It focuses on leveraging AI Foundry and other analytics tools to implement solutions for text-to-SQL and speech-to-SQL problems.

## Features
The project explores different tools and architectures, including:

*   **Fine-tuning:** Adapting pre-trained models to specific SQL generation tasks.
*   **Prompt Engineering:** Crafting effective prompts to guide large language models (LLMs) in generating accurate SQL queries.
*   **Retrieval-Augmented Generation (RAG):** Enhancing LLM responses by retrieving relevant information from knowledge bases (e.g., database schemas, documentation) before generation.

The primary goal is to provide practical examples and frameworks for solving complex analytics challenges using GenAI, specifically translating natural language (text or speech) into executable SQL queries.

### To be Done

- [ ] Add Bicep Templates to infra AI Foundry
- [ ] AI Search infra and connections
- [ ] Propagation of data in SQL databases (Postgres, SQL Server, MS Fabric Lakehouse and Warehouse, Databricks Serveless Warehouse)
- [ ] Tool to query in Database engines
- [ ] Tool to speech to SQL
- [ ] Semantic Kernel samples

## Getting Started

### Prerequisites

* **Azure Subscription:** You must have [Azure subscription](https://azure.microsoft.com/free/) with a valid payment method. Free or trial Azure subscriptions won't work. If you don't have an Azure subscription, create a paid Azure account to begin.
* Access to the Azure portal.
* An Azure AI Foundry project.
* **Permissions:** Ensure you have sufficient permissions to deploy resources within your subscription.**Azure role-based access controls (Azure RBAC)** are used to grant access to operations in Azure AI Foundry portal. To perform the steps in this article, your user account must be assigned the owner or contributor role for the Azure subscription. For more information on permissions, see Role-based access control in Azure AI Foundry portal.
* **Azure CLI:** Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) to interact with your Azure resources.
* **Bicep CLI:** Ensure the [Bicep CLI](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/install) is installed to compile and deploy your Bicep templates.
* **Visual Studio Code (Optional):** For an enhanced development experience, it is recommended to use [Visual Studio Code](https://code.visualstudio.com/) along with the Bicep extension.
* Python 3.12+
* [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver)


### Installation

1.  **Install uv:**
    If you don't have `uv` installed, follow the instructions on the [official uv installation guide](https://github.com/astral-sh/uv#installation). A common method is using pipx or pip:
    ```bash
    # Using pipx
    pipx install uv

    # Or using pip
    pip install uv
    ```

2.  **Create and Activate a Virtual Environment:**
    Use `uv` to create and activate a virtual environment. This isolates project dependencies.
    ```bash
    # Create a virtual environment named .venv
    uv venv

    # Activate the virtual environment
    # On Windows (Command Prompt/PowerShell)
    .venv\Scripts\activate
    # On macOS/Linux (bash/zsh)
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    With the virtual environment activated, use `uv` to install the dependencies listed in `pyproject.toml`.
    ```bash
    uv pip install -r pyproject.toml # Or if using pyproject.toml directly for dependencies
    ```

## Quickstart 

Below there are the steps to test **_manually_**.  

> **DISCLAIMER**: Currently some parts are manual but the idea is to automate lot of parts to help a quick test.

1. **Download Dataset and prepare it to Fine Tune:**
    To Download Dataset and prepare it for finetune just run the script.
    ```bash
    # Example: Running the data processing script
    uv python src/main.py
    ```
2.  **Azure Setup & Fine-tuning:**
    *   Go to the Azure portal.
    *   Create a new Resource Group.
    *   Create an AI Foundry resource within the Resource Group.
    *   Create an AI Foundry project.
    *   Create Azure AI Services in a region that supports fine-tuning for GPT-4o models (check Azure documentation for supported regions).
    *   Follow the fine-tuning instructions: [Azure AI Foundry Fine-tuning Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/fine-tune-serverless?tabs=chat-completion&pivots=foundry-portal)
    *   During fine-tuning, use the content from `assets/model_instructions/system_prompt_database_context.txt` as the system prompt (model instructions).
    *   After the fine-tuning job completes successfully, deploy the model.

3.  **Local Database Setup:**
    *   Download Olist [Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/code) at kaggle.
    *   Run the local PostgreSQL database using Docker Compose (see [Local Database](#local-database) section below for commands).
    *   Access pgAdmin (usually `http://localhost:15433`) using the credentials from your `.env` file.
    *   **Important:** Currently, the `init.sql` script might not automatically populate data due to potential `COPY` command limitations or permissions within Docker. If the tables are empty after starting the containers, manually execute the `CREATE TABLE` statements from `infra/dockercompose/init.sql` in pgAdmin. Then, use pgAdmin's import tool or `psql` to load the data from the CSV files located in the `data/olist_dataset` directory into the corresponding tables.

4.  **Test the Fine-tuned Model:**
    *   Interact with your deployed fine-tuned model endpoint.
    *   Ask natural language questions about the Olist dataset (see [Examples of queries](#examples-of-queries) below).
    *   Take the SQL query generated by the model.
    *   Execute the generated SQL query in pgAdmin against your local database.
    *   Verify the results are correct.

## Local Database 
This database can be used for testing text-to-SQL models locally.

The dataset used is *Brazilian E-Commerce Public Dataset by Olist* and can be download [here](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

1.  **Navigate to the Docker Compose directory:**
    ```bash
    cd infra/dockercompose
    ```

2.  **Start the database and pgAdmin services:**
    ```bash
    docker-compose up -d
    ```
    This command will:
    *   Pull the latest PostgreSQL and pgAdmin images if they are not already present.
    *   Create and start containers for the database (`database`) and a web-based administration tool (`pgadmin`).
    *   Mount the `init.sql` script, which creates the necessary tables and uses the `COPY` command to import data from the CSV files located in the `data/olist_dataset` directory into the PostgreSQL database.
    *   Mount the `data` directory into the database container so `init.sql` can access the CSV files.
    *   Use the environment variables defined in `envs/.env` for database credentials and pgAdmin setup.

    You can access pgAdmin at `http://localhost:15433` and connect to the PostgreSQL database running on `localhost:15432`. Refer to your `.env` file for login credentials.

3.  **To stop and remove the containers, network, and volumes:**
    ```bash
    docker-compose down -v
    ```

## Examples of queries
Here there are some questions and correct query to retrieve values. 

### Questions

#### Customers

Tell me what is the number of unique customer by state.

``` sql
SELECT customer_state,
       COUNT(customer_unique_id) AS no_of_customers
FROM customers
GROUP BY customer_state
ORDER BY no_of_customers DESC;
```

Tell me top 10 product categories most ordered by customers.

``` sql
WITH customer_items AS (SELECT *
                        FROM customers
                        JOIN orders USING(customer_id)
                        JOIN order_items USING(order_id)
                        JOIN products USING(product_id))
SELECT product_category,
       SUM(order_item_id) AS units
FROM customer_items
GROUP BY product_category
ORDER BY units DESC
LIMIT 10;
```

What is the frequency credit card payment by state?

```sql
WITH payment AS(SELECT customer_state,
                       payment_type
                FROM orders AS od
                JOIN customers AS cu USING(customer_id)
                JOIN order_payments AS pay USING(order_id))
SELECT customer_state,
       payment_type,
       COUNT(*)
FROM payment
WHERE payment_type = 'credit_card'
GROUP BY customer_state, payment_type
ORDER BY count DESC;
```

What is the proportion of customers paying in more than one installment by state? 

``` sql
SELECT customer_state,
       count,
       (count/total_order) AS proportion
FROM(WITH payment AS(SELECT customer_state,
                            payment_installments
                     FROM orders AS od
                     JOIN customers AS cu USING(customer_id)
                     JOIN order_payments AS pay USING(order_id)
                     WHERE payment_installments > 1)
    SELECT customer_state,
           COUNT(payment_installments)::real AS count,
           (SELECT COUNT(order_id) FROM orders)::real AS total_order
    FROM payment
    GROUP BY customer_state
    ORDER BY count DESC) AS g2
WHERE count > 1000
ORDER BY proportion DESC;
```

#### Sellers
Give me the number of sellers by state.

```sql
SELECT seller_state,
       number_of_sellers,
       RANK() OVER(ORDER BY number_of_sellers DESC)
FROM  (SELECT seller_state,
              COUNT(seller_id) AS number_of_sellers
       FROM sellers
       GROUP BY seller_state) AS nos
LIMIT 10;
```

What is the top 5 sellers by average shipping time?
```sql
WITH ship_interval AS(SELECT seller_id,
                          order_id,
                          EXTRACT(EPOCH FROM (order_delivered_carrier - order_purchase)::interval)/3600 AS delivery_interval,
                          EXTRACT(EPOCH FROM (shipping_limit_date - order_purchase)::interval)/3600 AS shipping_limit_interval
                      FROM(SELECT order_id,
                                  seller_id,
                                  order_purchase,
                                  order_delivered_carrier,
                                  shipping_limit_date
                           FROM order_items
                           JOIN orders USING(order_id)
                           JOIN sellers USING(seller_id)
                           WHERE order_status IN('delivered')) AS ship_time)
SELECT seller_id,
       AVG(delivery_interval)::real AS avg_del_time,
       AVG(shipping_limit_interval)::real AS ship_limit_time
FROM ship_interval
GROUP BY seller_id
ORDER BY avg_del_time 
LIMIT 5;
```

What is average sales per order by seller?
```sql
SELECT seller_id,
       avg_order_rev,
       RANK() OVER(ORDER BY avg_order_rev DESC) AS rank
FROM(WITH order_unit AS(SELECT seller_id,
                               price,
                               COUNT(order_id) AS total_orders,
                               SUM(order_item_id) AS total_units
                        FROM sellers
                        JOIN order_items USING(seller_id)
                        GROUP BY seller_id, price),
    seller_unique AS(SELECT seller_id,
                            (price*total_units)::real AS revenue,
                            total_orders
                     FROM order_unit)

    SELECT seller_id,
           (revenue/total_orders)::real AS avg_order_rev
    FROM seller_unique) AS seller_avg
LIMIT 10
```
#### Others

Give me the frequency number by payment type. 

```sql
SELECT ROW_NUMBER() OVER(ORDER BY frequency DESC),
       payment_type,
       frequency
FROM(SELECT payment_type,
            COUNT(order_id) AS frequency
FROM order_payments
GROUP BY payment_type) AS freq
LIMIT 10
```
Give product translation

```sql
WITH prod_cat AS(SELECT DISTINCT(product_category)
                 FROM products)
SELECT product_category, category_translation
FROM prod_cat AS pc
LEFT JOIN product_translation AS pt
ON pc.product_category = pt.category
```

## Demo
### Finetunning Scenario
*TBD*
1.
2.
3.
### RAG
*TBD*
1.
2.
3.
### Both
*TBD*
1.
2.
3.
### MultiAgent
*TBD*
1.
2.
3.

## Techniques

### Promp-Engineering
Just get some Promptys files and run to check output is correct. 
<<TBD>>

### Fine-tunning
The file `main.py` get dataset from huggingface and parse it to save in jsonl format (this is only format that AI Foudry accepts), after it the code `upload_dataset.py`upload the files to storage account to be used for finetunning. The code `finetune.py` start finetune job using Azure SDK. 

After model is trained it is time to use model to run queries and get information of text to sql. 

### Retrieval-Augmented Generation (RAG)
<<TBD>>

### All togheter now
This approach will be used to join approaches to show results. 

### Comparison
Here there are a performance comparison of techniques. 


## Resources

- [Customize a model with fine-tuning](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/fine-tuning?context=%2Fazure%2Fai-studio%2Fcontext%2Fcontext&tabs=azure-openai&pivots=programming-language-studio)
- [NL to SQL Architecture Alternatives](https://techcommunity.microsoft.com/blog/azurearchitectureblog/nl-to-sql-architecture-alternatives/4136387)
- [https://learn.microsoft.com/en-us/training/modules/finetune-model-copilot-ai-studio/4-finetune-model](https://learn.microsoft.com/en-us/training/modules/finetune-model-copilot-ai-studio/4-finetune-model)
- [Azure OpenAI Service models](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models?tabs=global-standard%2Cstandard-chat-completions)
- [Azure OpenAI GPT-4o-mini fine-tuning tutorial](https://learn.microsoft.com/en-us/azure/ai-services/openai/tutorials/fine-tune?tabs=command-line)
- [Dataset](https://huggingface.co/datasets/agentlans/sql-text-collection)
- [Fine-Tuning LLM for SQL Query Generation](https://github.com/imanoop7/fine-tuning-llm-for-SQL-query-generation/tree/main)
- [kaggle-sql-xp-phi-3-mini-4k-instruct](https://github.com/Spectrewolf8/SQL-PHI--PHi-3-SQL-generation-fine-tune-experiment)
- [gbb-fine-tuning-azure-oai](https://github.com/Azure-Samples/gbb-fine-tuning-azure-oai/tree/main)
- [azure-nl2sql-accelerator](https://github.com/vhoudebine/azure-nl2sql-accelerator)
- [NL2SQL_Handbook](https://github.com/HKUSTDial/NL2SQL_Handbook)
- [Fine-Tuning Language Models for Context-Specific SQL Query Generation](https://paperswithcode.com/paper/fine-tuning-language-models-for-context)
- [fine-tuning-direct-preference-optimization](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/fine-tuning-direct-preference-optimization)
- [Docker-compose reference: docker-compose-postgres](https://github.com/felipewom/docker-compose-postgres/tree/main)
- [Olist Queries Reference: olist_full_sql](https://github.com/Marty-McLeod/olist_full_sql/tree/main)

## Contributing

[Contributing](CONTRIBUTING.md)

## License

[MIT License](LICENSE.md)

