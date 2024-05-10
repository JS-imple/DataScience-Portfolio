# Google-Advanced-Data-Analytics-Professional-Capstone-Project
Description and deliverables
This capstone project is an opportunity for you to analyze a dataset and build predictive models that can provide insights to the Human Resources (HR) department of a large consulting firm.

Upon completion, you will have two artifacts that you would be able to present to future employers. One is a brief one-page summary of this project that you would present to external stakeholders as the data professional in Salifort Motors. The other is a complete code notebook provided here. Please consider your prior course work and select one way to achieve this given project question. Either use a regression model or machine learning model to predict whether or not an employee will leave the company. The exemplar following this actiivty shows both approaches, but you only need to do one.

In your deliverables, you will include the model evaluation (and interpretation if applicable), a data visualization(s) of your choice that is directly related to the question you ask, ethical considerations, and the resources you used to troubleshoot and find answers or solutions.


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Pace: Plan

The HR department at Salifort Motors wants to take some initiatives to improve employee satisfaction levels at the company. They collected data from employees, but now they don’t know what to do with it. They refer to you as a data analytics professional and ask you to provide data-driven suggestions based on your understanding of the data. They have the following question: what’s likely to make the employee leave the company?

Your goals in this project are to analyze the data collected by the HR department and to build a model that predicts whether or not an employee will leave the company.

If you can predict employees likely to quit, it might be possible to identify factors that contribute to their leaving. Because it is time-consuming and expensive to find, interview, and hire new employees, increasing employee retention will be beneficial to the company.

# pAce: Data Exploration (Initial EDA and data cleaning)

- Understand your variables
- Clean your dataset (missing data, redundant data, outliers)

# paCe: Construct Stage
- Determine which models are most appropriate
- Construct the model
- Confirm model assumptions
- Evaluate model results to determine how well your model fits the data

# pacE: Execute Stage
- Interpret model performance and results
- Share actionable steps with stakeholders


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Summary of model results
Logistic regession
model metrics achieved: precision of 80%, recall of 83%, f1-score of 80% (all weighted averages). Accuracy of 83%, on the test set.

Tree-based Machine Learning
With feature engineering, the Decision three achieved: precision of 87.0%, recall of 90.4%, f1-score of 88.7%, and accuracy of 96.2%, AUC of 93.8%, on the test set. The random forest modestly outperformed the decision tree model.
Conclusion, Recommendations, Next Steps
The models and the feature importances extracted from the modeles can confirm that employees at the company are overworked.

For future employeee retention these recommendations could be presented

Number of projects cutoff point
Promoting employees who have been at the company for at least 4 years or check reason for satifaction for employees with 4 year tenure
Do not require employees to work longer hours or compensate them accordingly
Make clear about expectation about workload, possibly inform about overtime pay policies.
Company wide and in teams discussion about company work culture, look in to speicfics for each team.
Evaluation scores should not be reseved for employees with 200+ hours per month. Rescale for employees who contrubte more.
