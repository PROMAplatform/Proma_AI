implicit_template = """
Please answer as if you were the speaker and the user was the listener.
Don't rely too much on history and prompt.
Do not enter settings yourself that are not in the prompt.
If it is correct to answer the user's question using a prompt, generate an answer using the prompt. If it is not correct, generate an answer corresponding to the user's question without using the prompt.
If you want to emphasize numbers in Markdown when replying in list format, enclose the numbers in Markdown symbols, like **number.content**.
Never use ** markdown after a number; instead, put the number inside ** markdown.
"""

korean_template = """
!!! Answer only in Korean!!!
"""

eval_coh_template = """
You will be given a prompt, a user question, and the corresponding output generated in response to the user's question.

Your task is to rate the output on one metric.

Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

Coherence (1-5) - The overall quality of the response in terms of structure and organization. The response should be well-structured and logically organized, building from sentence to sentence to form a coherent body of information that effectively addresses the prompt and the user question.

Evaluation Steps:

1. Read the prompt and user question carefully to identify the main goal and key requirements.
2. Read the output and compare it to both the prompt and user question. Check if the response addresses the main goal and requirements of the prompt, and if the information is presented clearly and logically.
3. Ensure that the response is well-structured, with sentences and ideas flowing smoothly from one to the next.
4. Assign a coherence score from 1 to 5, where 1 is the lowest and 5 is the highest based on the Evaluation Criteria.

---

Example:

Prompt:  
{Prompt}

User Question:  
{User Question}

Output:  
{Output}

---

Evaluation Form (scores ONLY):

---
"""

eval_con_template = """
You will be given a prompt, a user question, and the corresponding output generated from the prompt in response to the user’s question.

Your task is to rate the output on one metric.

Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

Consistency (1-5) - The factual alignment between the output and the prompt/user question. A factually consistent output contains only statements that are supported by the information provided in the prompt and directly answer the user question. Penalize outputs that contain fabricated or unsupported information.

Evaluation Steps:

	1.	Read the prompt and user question carefully and identify the main facts and requirements they present.
	2.	Read the output and compare it to both the prompt and the user question. Check if the output contains any factual errors or misalignments with the prompt and if it correctly addresses the user question.
	3.	Assign a score for consistency based on the Evaluation Criteria, with 1 being the lowest and 5 being the highest.

Example:

Prompt:
{Prompt}

User Question:
{User Question}

Output:
{Output}

Evaluation Form (scores ONLY):

"""

eval_flu_template = """
You will be given a prompt, a **user question**, and the corresponding **output** generated in response to the user’s question.

Your task is to rate the output on one metric.

Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

Fluency (1-3) - The overall quality of the generated content in terms of grammar, spelling, punctuation, word choice, and sentence structure.

- 1: Poor. The content has many grammatical errors, making it hard to understand or unnatural in expression.
- 2: Fair. The content has some grammatical errors that affect clarity, but the key points are still understandable.
- 3: Good. The content has few or no grammatical issues, making it easy to read and follow.

Evaluation Steps:

1. Read the prompt and user question carefully.
2. Read the output and assess its grammatical correctness, punctuation, and sentence structure.
3. Evaluate how easily the output reads and how naturally the information flows.
4. Assign a fluency score from 1 to 3, based on the Evaluation Criteria.

---

Example:

Prompt:  
{Prompt}

User Question:  
{User Question}

Output:  
{Output}

---

Evaluation Form (scores ONLY):

"""

eval_rel_template = """
You will be given a prompt, a user question, and the corresponding output generated in response to the user’s question.

Your task is to rate the output on one metric.

Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

Relevance (1-5) - The degree to which the generated content includes only important information. Penalize if there are irrelevant details, redundancies, or omitted key points that are critical for answering the user question.

	•	1: The response contains irrelevant details, redundancies, or omits key points that are important.
	•	2: The response includes some irrelevant details or missing key points, but the main focus is still understandable.
	•	3: The response is relevant and includes important points with minimal irrelevant information.
	•	4: The response stays on-topic and includes all the critical information with no irrelevant details.
	•	5: The response is perfectly aligned with the prompt and the user question, including all key information while excluding any unnecessary details.

Evaluation Steps:

	1.	Read the prompt and user question carefully to understand the main requirements and key points.
	2.	Read the output and compare it to the prompt and user question.
	3.	Ensure the output addresses the key points clearly without including irrelevant details, redundancies, or omitting critical information.
	4.	Assign a relevance score from 1 to 5 based on how well the output aligns with the key points and requirements.

Example:

Prompt:
{Prompt}

User Question:
{User Question}

Output:
{Output}

Evaluation Form (scores ONLY):
"""

eval_comment_template = """
Prompt: {prompt}

Based on the provided prompt evaluate the quality of the output considering the following criteria:

1. Coherence(1-5): How well-structured and logically organized is the response? Does it flow naturally from one idea to the next?
    - Coherence Score: {Coherence}
2. Consistency(1-5): Does the output remain factually accurate and align with the information presented in the prompt and user question? Are there any inconsistencies or errors?
    - Consistency Score: {Consistency}
3. Fluency(1-3): How smooth and easy to understand is the response in terms of grammar, punctuation, and sentence structure? Does it feel natural to read?
    - Fluency Score: {Fluency}
4. Relevance(1-5): Does the response stay focused on the key points, avoiding irrelevant details or redundancies?
    - Relevance Score: {Relevance}

Provide a concise summary of the overall quality of the prompt, incorporating assessments of coherence, consistency, fluency, and relevance.
Also include comments on how the prompt could be improved.
Please answer in Korean, and keep your answer to 3 or 4 sentences, not too long.
"""

image_desc_template = """
Describe the information in this image in detail in natural language. 
The more detailed the better, because you will have to look at the natural language information and process the answer.
"""

image_template = """
The user has now entered a question along with an image. 
I will provide information about the image in natural language, so please refer to this and answer.
image description:
"""