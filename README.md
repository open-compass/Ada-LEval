# 📖Ada-LEval: Evaluating long-context LLMs with length-adaptable benchmarks

**Ada-LEval** is a pioneering benchmark to assess the long-context capabilities with length-adaptable questions. It comprises two challenging tasks: **TSort**, which involves arranging text segments into the correct order, and **BestAnswer**, which requires choosing the best answer of a question among multiple candidates.

Both tasks feature the following advantages:
1. **Controllable Test Cases**: The length of each test case can be finely tuned - by adjusting the number and length of text segments in TSort and altering the number of distractor options in BestAnswer. 
2. **Necessity for Full-Text Comprehension**: Successful completion of both tasks mandates complete reading and understanding of the provided text.
3. **Precise Accuracy Measurement**: The design of these tasks allows for unambiguous accuracy calculation. TSort has a definitive 'correct' order, while in BestAnswer, the annotated responses by the questioner serve as definitive answers.

![AdaLEval_Demo](https://github.com/kennymckormick/Ada-LEval/assets/75252858/776aab87-b770-46c5-85a1-7915ee8a7902)

## 📊Evaluation Result
Here is the evaluation result of TSort and BestAnswer benchmark. We also provide a 'random guess' baseline for each task. 

### Long-Context Settings
| TSort                | 2k   | 4k   | 8k  | 16k |
|----------------------|------|------|-----|-----|
| GPT-4-Turbo          | 18.5 | 15.5 | 7.5 | 3.5 |
| GPT-3.5-Turbo-1106   | 4.0  | 4.5  | 4.5 | 5.5 |
| Claude-2             | 5.0  | 5.0  | 4.5 | 3.0 |
| LongChat-7b-v1.5-32k | 5.3  | 5.0  | 3.1 | 2.5 |
| ChatGLM2-6B-32k      | 0.9  | 0.7  | 0.2 | 0.9 |
| ChatGLM3-6B-32k      | 2.3  | 2.4  | 2.0 | 0.7 |
| Vicuna-7b-v1.5-16k   | 5.3  | 2.2  | 2.3 | 1.7 |
| Vicuna-13b-v1.5-16k  | 5.4  | 5.0  | 2.4 | 3.1 |
| Random Guess         | 4.2  | 4.2  | 4.2 | 4.2 |


| BestAnswer           | 1k   | 2k   | 4k   | 6k   | 8k   | 12k  | 16k  |
|----------------------|------|------|------|------|------|------|------|
| GPT-4-Turbo          | 74.0 | 73.5 | 67.5 | 59.5 | 53.5 | 49.5 | 44.0 |
| GPT-3.5-Turbo-1106   | 61.5 | 48.5 | 41.5 | 29.5 | 17.0 | 2.5  | 2.5  |
| Claude-2             | 65.0 | 43.5 | 23.5 | 15.0 | 17.0 | 12.0 | 11.0 |
| LongChat-7b-v1.5-32k | 32.4 | 10.7 | 5.7  | 3.1  | 1.9  | 1.6  | 0.8  |
| ChatGLM2-6B-32k      | 31.2 | 10.9 | 4.5  | 1.6  | 1.6  | 0.0  | 0.3  |
| ChatGLM3-6B-32k      | 39.8 | 18.8 | 9.0  | 5.0  | 3.4  | 0.9  | 0.5  |
| Vicuna-7b-v1.5-16k   | 37.0 | 11.1 | 5.8  | 3.2  | 1.8  | 1.9  | 1.0  |
| Vicuna-13b-v1.5-16k  | 53.4 | 29.2 | 13.1 | 4.3  | 2.2  | 1.4  | 0.9  |
| Random Guess         | 26.7 | 10.1 | 4.5  | 3.0  | 2.3  | 1.4  | 1.1  |

### Ultra-Long-Context Settings
| TSort        | 32k           | 64k          | 128k         |
|--------------|---------------|--------------|--------------|
| GPT-4-Turbo  | 6.0    | 6.0 | 6.0 |
| Claude-2     | 0.0           | 0.0          | /            |
| Claude-2.1   | 0.0           | 0.0          | 0.0          |
| Random Guess | 4.2           | 4.2          | 4.2          |

| BestAnswer       | 32k           | 64k | 128k |
| ----------- | ------------- | --- | ---- |
| GPT-4-Turbo | 6.0 | 0.0 | 0.0  |
| Claude-2      | 4.0 | 0.0  | /   |
| Claude-2.1    | 4.0 | 0.0  | 0.0 |
| Random Guess  | 0.6 | 0.3  | 0.1 |
## 💻How to evaluate on Ada-LEval
To be updated.

## 🖊️Citation
To be updated.