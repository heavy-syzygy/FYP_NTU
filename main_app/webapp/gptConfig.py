import openai
from textwrap import dedent
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def prompt(user_input):
    DEFAULT_PROMPT = dedent(
        f"""
        Please extract aspect categories, aspect terms, related segments and related sentiments from the following text and format output in JSON:

        This product is easy to use but expensive. It is still ok though.

        [
          {{"aspect": "Product", "category": "Usability", "segment": "This product is easy to use", "sentiment": "Positive"}}.
          {{"aspect": "Product", "category": "Price", "segment": "expensive", "sentiment": "Negative"}},
          {{"aspect": "Product", "category": "General", "segment": "It is still ok though", "sentiment": "Neutral"}}
        ]
    """
    )
    if user_input and user_input!='':
        sen_list = []
        for item in user_input:
            if len(item) == 5:
                string = dedent(
                """\
                {}

                [
                  {{ "aspect": "{}", "category": "{}", "segment": "{}", "sentiment": "{}" }}
                ]""".format(*item))
                sen_list.append(string)

            elif len(item) == 9:
                string = dedent(
                """\
                {}

                [
                  {{ "aspect": "{}", "category": "{}", "segment": "{}", "sentiment": "{}" }},
                  {{ "aspect": "{}", "category": "{}", "segment": "{}", "sentiment": "{}" }}
                ]""".format(*item))
                sen_list.append(string)

            elif len(item) == 13:
                string = dedent(
                """\
                {}

                [
                  {{ "aspect": "{}", "category": "{}", "segment": "{}", "sentiment": "{}" }},
                  {{ "aspect": "{}", "category": "{}", "segment": "{}", "sentiment": "{}" }},
                  {{ "aspect": "{}", "category": "{}", "segment": "{}", "sentiment": "{}" }}
                ]""".format(*item))
                sen_list.append(string)


        if len(sen_list) ==1:
            ABSA_PROMPT = dedent(
                """\
                Please extract aspect categories, aspect terms, related segments and related sentiments from the following text and format output in JSON:

                {}\

            """
            ).format(sen_list[0])
        elif len(sen_list) ==2:
            ABSA_PROMPT = dedent(
                """\
                Please extract aspect categories, aspect terms, related segments and related sentiments from the following text and format output in JSON:

                {}

                {}\
            """
                ).format(sen_list[0], sen_list[1])
        elif len(sen_list) ==3:
            ABSA_PROMPT = dedent(
                """\
                Please extract aspect categories, aspect terms, related segments and related sentiments from the following text and format output in JSON:

                {}

                {}

                {}\
            """
                ).format(sen_list[0], sen_list[1], sen_list[2])
        else:
            return DEFAULT_PROMPT
    else:
        return DEFAULT_PROMPT
    return ABSA_PROMPT




def analyze(
    text,
    prompt_text,
    extra_prompt="",
    temperature=0.5,
    max_tokens=1024,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
):
    final_prompt = f"{prompt_text}\n{extra_prompt}\n{text}"
    # print(prompt_text)
    return openai.Completion.create(
        model="text-davinci-002",
        prompt=final_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
# if __name__ == '__main__':
