import json
import openai
from openai import OpenAI
import httpx
import os
from time import sleep
import random
from sentence_transformers import SentenceTransformer, util

client = OpenAI(
    base_url="",
    api_key="",
    http_client=httpx.Client(
        base_url="",
        follow_redirects=True,
    ),
)

model = SentenceTransformer("all-MiniLM-L6-v2")
PROMPT_TEMPLATES = {
    "Role-Playing Type": """Please rephrase the following role-playing question to sound more natural, fluent, and conversational. Keep the meaning and scenario intact. The reader is asked to imagine themselves in the described situation. 
### Requirements:
Make sure you use the right pronouns.
Please do not miss any Question information, including scene details.
Avoid changing the intent or adding new information.
**Only output the rewritten text**.
###Question: 
[QUESTION]
""",

    "Advice Type": """Please rewrite the following advice-seeking question to make it sound more natural and fluent, as if a real person were asking it in a social setting.Keep the meaning and scenario intact.
It should be noted that advice needs to be provided to the main character.
### Requirements:
Please do not miss any Question information, including scene details.
Avoid changing the intent or adding new information.
**Only output the rewritten text**.
###Question: 
[QUESTION]
""",

    "Behavior Evaluation Type": """Paraphrase the following question to improve fluency and naturalness, while keeping its meaning and scenario intact. The question is about evaluating whether a certain action taken by the character is reasonable.Maintain neutrality and do not introduce judgmental language.
### Requirements:
Use "reasonable".
Make sure you use the right pronouns.
Please do not miss any Question information, including scene details.
Avoid changing the intent or adding new information.
**Only output the rewritten text**.
###Question: 
[QUESTION]
"""
}


def paraphrase_question(template_type, original_question, retries=3):
    prompt_template = PROMPT_TEMPLATES.get(template_type)
    if not prompt_template:
        print(f"未找到类型 {template_type} 的提示词，使用原始问题")
        return original_question, 0

    prompt = prompt_template.replace("[QUESTION]", original_question)

    for _ in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
            )
            return response.choices[0].message.content.strip(), response.usage.total_tokens if hasattr(response,
                                                                                                       'usage') else 0
        except Exception as e:
            print(f"改写失败，重试中: {e}")
            sleep(0.5)
    return original_question, 0


# 相似度计算
def calculate_similarity(original, paraphrased):
    embedding1 = model.encode(original, convert_to_tensor=True)
    embedding2 = model.encode(paraphrased, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
    return similarity


def postprocess_low_similarity(input_file, output_file, min_similarity=0.8, max_retry=5):
    results = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            item = json.loads(line.strip())
            original = item['original_question']
            paraphrased = item['paraphrased_question']
            similarity = item['similarity']
            template_type = item['template_type']

            retry_count = 0
            while similarity < min_similarity and retry_count < max_retry:
                print(f"[{idx}] 相似度 {similarity:.4f} < {min_similarity}，正在重新改写（第 {retry_count + 1} 次）...")
                paraphrased, _ = paraphrase_question(template_type, original)
                similarity = calculate_similarity(original, paraphrased)
                print(f"新相似度：{similarity:.4f}")
                retry_count += 1
                sleep(0.5)  # 避免频繁调用API

            # 更新字段
            item['paraphrased_question'] = paraphrased
            item['similarity'] = similarity
            results.append(item)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as fout:
        for item in results:
            fout.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"后处理完成，共处理 {len(results)} 条数据，已保存至 {output_file}")


#忘记保存维度了
def m_q_s(s, input, output):
    # 加载场景数据，获得 id 到 dimension 映射
    with open(s, "r", encoding="utf-8") as sf:
        scenarios = json.load(sf)
        scenario_dim_map = {s["id"]: s["dimension"] for s in scenarios}

    with open(input, "r", encoding="utf-8") as infile, \
            open(output, "w", encoding="utf-8") as outfile:

        for line in infile:
            item = json.loads(line.strip())
            sid = item.get("scenario_id")

            # 查找对应的 dimension
            dimension = scenario_dim_map.get(sid)
            if dimension:
                item["dimension"] = dimension
            else:
                print(f"未找到场景 {sid} 对应的维度。")

            outfile.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("处理完成")


# 主流程
def main():
    input_file = ""
    output_file = ""
    total_tokens = 0
    results = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line.strip())
                original_question = item['question']
                template_type = item['template_type']
                question_id = item.get('question_id')
                scenario_id = item.get('scenario_id')

                # 改写
                paraphrased_question, tokens = paraphrase_question(template_type, original_question)
                total_tokens += tokens
                print(f"{question_id} done")
                # 相似度
                similarity = calculate_similarity(original_question, paraphrased_question)
                print(f"{similarity} done")
                results.append({
                    "question_id": question_id,
                    "scenario_id": scenario_id,
                    "template_type": template_type,
                    "original_question": original_question,
                    "paraphrased_question": paraphrased_question,
                    "similarity": similarity
                })

            except Exception as e:
                print(f"处理失败: {e}\n原始数据: {line}")
                continue

    with open(output_file, "w", encoding="utf-8") as fout:
        for item in results:
            fout.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"改写完成，共处理 {len(results)} 条，累计 tokens 使用量: {total_tokens}")

    postprocess_low_similarity("", "")
    m_q_s("","","")


if __name__ == "__main__":
    main()
