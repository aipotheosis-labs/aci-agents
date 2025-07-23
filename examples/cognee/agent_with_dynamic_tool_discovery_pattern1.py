import cognee
import asyncio
import os
from cognee.api.v1.visualize.visualize import visualize_graph
from cognee.modules.search.types import SearchType
import json
from dotenv import load_dotenv

from aci import ACI
from aci.meta_functions import ACISearchFunctions
from aci.types.functions import FunctionDefinitionFormat
from openai import OpenAI

from cognee.shared.data_models import KnowledgeGraph
from cognee.modules.data.models import Dataset, Data
from cognee.modules.data.methods.get_dataset_data import get_dataset_data
from cognee.modules.cognify.config import get_cognify_config
from cognee.modules.pipelines.tasks.task import Task
from cognee.modules.pipelines import run_tasks
from cognee.modules.users.models import User
from cognee.tasks.documents import (
    check_permissions_on_dataset,
    classify_documents,
    extract_chunks_from_documents,
)
from cognee.infrastructure.llm import get_max_chunk_tokens
from cognee.tasks.graph import extract_graph_from_data
from cognee.tasks.storage import add_data_points
from cognee.tasks.summarization import summarize_text

from cognee.modules.users.methods import get_default_user
from cognee.modules.data.methods import get_datasets_by_name
from cognee.modules.users.methods import get_user


job_position = """Senior Data Scientist (Machine Learning)

Company: TechNova Solutions
Location: San Francisco, CA

Job Description:

TechNova Solutions is seeking a Senior Data Scientist specializing in Machine Learning to join our dynamic analytics team. The ideal candidate will have a strong background in developing and deploying machine learning models, working with large datasets, and translating complex data into actionable insights.

Responsibilities:

Develop and implement advanced machine learning algorithms and models.
Analyze large, complex datasets to extract meaningful patterns and insights.
Collaborate with cross-functional teams to integrate predictive models into products.
Stay updated with the latest advancements in machine learning and data science.
Mentor junior data scientists and provide technical guidance.
Qualifications:

Master’s or Ph.D. in Data Science, Computer Science, Statistics, or a related field.
5+ years of experience in data science and machine learning.
Proficient in Python, R, and SQL.
Experience with deep learning frameworks (e.g., TensorFlow, PyTorch).
Strong problem-solving skills and attention to detail.
Candidate CVs
"""

job_1 = """
CV 1: Relevant
Name: Dr. Emily Carter
Contact Information:

Email: emily.carter@example.com
Phone: (555) 123-4567
Summary:

Senior Data Scientist with over 8 years of experience in machine learning and predictive analytics. Expertise in developing advanced algorithms and deploying scalable models in production environments.

Education:

Ph.D. in Computer Science, Stanford University (2014)
B.S. in Mathematics, University of California, Berkeley (2010)
Experience:

Senior Data Scientist, InnovateAI Labs (2016 – Present)
Led a team in developing machine learning models for natural language processing applications.
Implemented deep learning algorithms that improved prediction accuracy by 25%.
Collaborated with cross-functional teams to integrate models into cloud-based platforms.
Data Scientist, DataWave Analytics (2014 – 2016)
Developed predictive models for customer segmentation and churn analysis.
Analyzed large datasets using Hadoop and Spark frameworks.
Skills:

Programming Languages: Python, R, SQL
Machine Learning: TensorFlow, Keras, Scikit-Learn
Big Data Technologies: Hadoop, Spark
Data Visualization: Tableau, Matplotlib
"""

job_2 = """
CV 2: Relevant
Name: Michael Rodriguez
Contact Information:

Email: michael.rodriguez@example.com
Phone: (555) 234-5678
Summary:

Data Scientist with a strong background in machine learning and statistical modeling. Skilled in handling large datasets and translating data into actionable business insights.

Education:

M.S. in Data Science, Carnegie Mellon University (2013)
B.S. in Computer Science, University of Michigan (2011)
Experience:

Senior Data Scientist, Alpha Analytics (2017 – Present)
Developed machine learning models to optimize marketing strategies.
Reduced customer acquisition cost by 15% through predictive modeling.
Data Scientist, TechInsights (2013 – 2017)
Analyzed user behavior data to improve product features.
Implemented A/B testing frameworks to evaluate product changes.
Skills:

Programming Languages: Python, Java, SQL
Machine Learning: Scikit-Learn, XGBoost
Data Visualization: Seaborn, Plotly
Databases: MySQL, MongoDB
"""
job_3 = """
CV 3: Relevant
Name: Sarah Nguyen
Contact Information:

Email: sarah.nguyen@example.com
Phone: (555) 345-6789
Summary:

Data Scientist specializing in machine learning with 6 years of experience. Passionate about leveraging data to drive business solutions and improve product performance.

Education:

M.S. in Statistics, University of Washington (2014)
B.S. in Applied Mathematics, University of Texas at Austin (2012)
Experience:

Data Scientist, QuantumTech (2016 – Present)
Designed and implemented machine learning algorithms for financial forecasting.
Improved model efficiency by 20% through algorithm optimization.
Junior Data Scientist, DataCore Solutions (2014 – 2016)
Assisted in developing predictive models for supply chain optimization.
Conducted data cleaning and preprocessing on large datasets.
Skills:

Programming Languages: Python, R
Machine Learning Frameworks: PyTorch, Scikit-Learn
Statistical Analysis: SAS, SPSS
Cloud Platforms: AWS, Azure
"""
job_4 = """
CV 4: Not Relevant
Name: David Thompson
Contact Information:

Email: david.thompson@example.com
Phone: (555) 456-7890
Summary:

Creative Graphic Designer with over 8 years of experience in visual design and branding. Proficient in Adobe Creative Suite and passionate about creating compelling visuals.

Education:

B.F.A. in Graphic Design, Rhode Island School of Design (2012)
Experience:

Senior Graphic Designer, CreativeWorks Agency (2015 – Present)
Led design projects for clients in various industries.
Created branding materials that increased client engagement by 30%.
Graphic Designer, Visual Innovations (2012 – 2015)
Designed marketing collateral, including brochures, logos, and websites.
Collaborated with the marketing team to develop cohesive brand strategies.
Skills:

Design Software: Adobe Photoshop, Illustrator, InDesign
Web Design: HTML, CSS
Specialties: Branding and Identity, Typography
"""
job_5 = """
CV 5: Not Relevant
Name: Jessica Miller
Contact Information:

Email: jessica.miller@example.com
Phone: (555) 567-8901
Summary:

Experienced Sales Manager with a strong track record in driving sales growth and building high-performing teams. Excellent communication and leadership skills.

Education:

B.A. in Business Administration, University of Southern California (2010)
Experience:

Sales Manager, Global Enterprises (2015 – Present)
Managed a sales team of 15 members, achieving a 20% increase in annual revenue.
Developed sales strategies that expanded customer base by 25%.
Sales Representative, Market Leaders Inc. (2010 – 2015)
Consistently exceeded sales targets and received the 'Top Salesperson' award in 2013.
Skills:

Sales Strategy and Planning
Team Leadership and Development
CRM Software: Salesforce, Zoho
Negotiation and Relationship Building
"""

job_6 = """
CV 6: Relevant
Name: Jamie Ogundiran
Contact Information:

Email: jamie.ogundiran@aipolabs.xyz
Phone: +44 07517177883
LinkedIn: https://www.linkedin.com/in/jamie-ogundiran-874aa3230/
GitHub: github.com/JamieO
Location: London, England
Summary:

Junior AI Engineer with 2+ years of experience in machine learning and data science. Recent graduate with strong foundation in Python, deep learning, and cloud technologies. Eager to contribute to AI product development.
Education:

Master of Science in Artificial Intelligence, Sapienza University of Rome (2022)
Bachelor of Science in Computer Science, University of Bologna (2020)
Experience:

Junior AI Engineer, StartupAI S.r.l. (Jun 2022 - Present)
Developed machine learning models for customer segmentation.
Built data preprocessing pipelines for structured and unstructured data.
Collaborated with senior engineers on model deployment strategies.
Participated in code reviews and agile development processes.
AI Intern, TechInnovate Italia (Jan 2022 - May 2022)
Implemented computer vision models for object detection.
Assisted in data collection and annotation for training datasets.
Conducted experiments on hyperparameter tuning and model optimisation.
Presented findings to technical and non-technical stakeholders.
Skills:

Programming Languages: Python, R, SQL, JavaScript, Java
ML/AI: TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy
Cloud: AWS (SageMaker, Lambda, S3), Google Colab
Tools: Jupyter, Git, Docker, VS Code, Anaconda
Databases: PostgreSQL, MongoDB, SQLite
Certifications:

AWS Certified Cloud Practitioner
Google AI Platform Fundamentals
Projects:

Image Classification Web App: Built end-to-end application using React and Flask.
Sentiment Analysis API: Deployed NLP model on AWS Lambda.
Recommendation System: Created collaborative filtering model for e-commerce.
"""

job_7 = """
CV 7: Relevant
Name: David Kim
Contact Information:

Email: david.kim@email.com
Phone: +31 20 123 4567
LinkedIn: linkedin.com/in/davidkim
GitHub: github.com/dkim
Location: Amsterdam, Netherlands
Summary:

Senior AI Engineer with 7+ years of experience in machine learning, deep learning, and AI product development. Expert in MLOps, model deployment, and leading AI teams in production environments.
Education:

PhD in Machine Learning, University of Amsterdam (2017)
Master of Science in Computer Science, ETH Zurich (2014)
Experience:

Senior AI Engineer, AI Innovations B.V. (Jan 2020 - Present)
Led team of 8 AI engineers developing conversational AI products.
Architected MLOps platform serving 100+ models in production.
Implemented LLM fine-tuning pipeline reducing training time by 70%.
Designed A/B testing framework for ML model performance evaluation.
AI Engineer, TechGiant Europe (Jun 2017 - Dec 2019)
Developed recommendation systems processing 1B+ user interactions.
Built real-time fraud detection models with 99.5% accuracy.
Mentored junior engineers and established ML best practices.
Published 3 research papers on deep learning optimisation.
Skills:

Programming Languages: Python, C++, Java, R, Scala, SQL
ML/AI: TensorFlow, PyTorch, Keras, XGBoost, Hugging Face
Cloud: AWS (SageMaker, Bedrock, Lambda), Azure ML, GCP
Tools: Docker, Kubernetes, MLflow, Kubeflow, Apache Airflow
Specialties: NLP, Computer Vision, Reinforcement Learning, LLMs
Certifications:

AWS Certified Machine Learning - Specialty
Google Cloud Professional ML Engineer
NVIDIA Deep Learning Institute Certification
"""

load_dotenv()

LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

openai = OpenAI()
aci = ACI()

BATCH_SIZE = 10
DATASET_NAME = "example"
MODEL_NAME = "gpt-4.1"

async def run_cognify_pipeline(dataset: Dataset, user: User = None):
    data_documents: list[Data] = await get_dataset_data(dataset_id=dataset.id)

    try:
        cognee_config = get_cognify_config()

        tasks = [
            Task(classify_documents),
            Task(check_permissions_on_dataset, user=user, permissions=["write"]),
            Task(
                extract_chunks_from_documents, max_chunk_size=get_max_chunk_tokens()
            ),  # Extract text chunks based on the document type.
            Task(
                extract_graph_from_data, graph_model=KnowledgeGraph,
                task_config={"batch_size": BATCH_SIZE}
            ),  # Generate knowledge graphs from the document chunks.
            Task(
                summarize_text,
                summarization_model=cognee_config.summarization_model,
                task_config={"batch_size": BATCH_SIZE},
            ),
            Task(add_data_points, task_config={"batch_size": BATCH_SIZE}),
        ]

        pipeline_run = run_tasks(tasks, dataset.id, data_documents, user, "cognify_pipeline", context={"dataset": dataset})
        pipeline_run_status = None

        async for run_status in pipeline_run:
            pipeline_run_status = run_status

    except Exception as error:
        raise error

async def main():

    prompt = (
    "You are a HR and Talent Management assistant with access to a unlimited number of tools via a meta function: "
    "ACI_SEARCH_FUNCTIONS"
    "You can use ACI_SEARCH_FUNCTIONS to find relevant functions across GMAIL and GOOGLE DOCS."
    "Once you have identified the functions you need to use, you can append them to the tools list and use them in future tool calls."
    "You are given a list of candidates and their information as a relevant context. use this context to help you answer the user's question."
    )

    tools_meta = [
        ACISearchFunctions.to_json_schema(FunctionDefinitionFormat.OPENAI),
    ]

    tools_retrieved: list[dict] = []

    chat_history: list[dict] = []

    # Cognee memory pipeline

    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    await cognee.add([job_1, job_2, job_3, job_4, job_5, job_6, job_7, job_position], DATASET_NAME)

    default_user = await get_default_user()

    user = await get_user(default_user.id)

    datasets = await get_datasets_by_name([DATASET_NAME], user.id)

    await run_cognify_pipeline(datasets[0], user)
        
    # Search the knowledge graph

    query = "1. Get information about David Kim 2. Create a new google doc 3. Add the information to google doc with 3 interview questions"
    retrieved_context = await cognee.search(query_type=SearchType.CHUNKS, query_text=query)
    print(f"\n\nretrieved_context\n\n{retrieved_context}\n\n")

    while True:
        print("Waiting for LLM Output")
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"{query}\n\nHere is some relevant context from your memory:\n{retrieved_context}",
                },
            ]
            + chat_history,
            tools=tools_meta + tools_retrieved,
            parallel_tool_calls=True,
        )
    
    # Process LLM response and potential function call
        content = response.choices[0].message.content
        print(content)
        tool_call = (
            response.choices[0].message.tool_calls[0]
            if response.choices[0].message.tool_calls
            else None
        )
        if content:
            print("LLM Message")
            print(content)
            chat_history.append({"role": "assistant", "content": content})

        # Handle function call if any
        if tool_call:
            print(f"Function Call: {tool_call.function.name}")
            print(f"arguments: {tool_call.function.arguments}")

            chat_history.append({"role": "assistant", "tool_calls": [tool_call]})
            result = aci.handle_function_call(
                tool_call.function.name,
                json.loads(tool_call.function.arguments),
                linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                allowed_apps_only=True,
                format=FunctionDefinitionFormat.OPENAI,
            )
            # if the function call is a get, add the retrieved function definition to the tools_retrieved
            if tool_call.function.name == ACISearchFunctions.get_name():
                tools_retrieved.extend(result)

            print("Function Call Result")
            print(result)
            # Continue loop, feeding the result back to the LLM for further instructions
            chat_history.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )
        else:
            # If there's no further function call, exit the loop
            print("Task Completed")
            break

if __name__ == '__main__':
    asyncio.run(main())