from typing import List

import numpy as np
import os
import requests
from FlagEmbedding import FlagModel
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

llm_origin = os.getenv('LLM_ORIGIN')

collection_name = "knowledge_collection"
qdrant_url = os.getenv('QDRANT_ORIGIN')
client = QdrantClient(qdrant_url)
source_code = '''import {
  createElement,
  createContext as reactCreateContext,
  useContext,
  useMemo,
  useRef,
} from 'react'
import type { ReactNode } from 'react'
import type { StoreApi } from 'zustand'
// eslint-disable-next-line import/extensions
import { useStoreWithEqualityFn } from 'zustand/traditional'

type UseContextStore<S extends StoreApi<unknown>> = {
  (): ExtractState<S>
  <U>(
    selector: (state: ExtractState<S>) => U,
    equalityFn?: (a: U, b: U) => boolean
  ): U
}

type ExtractState<S> = S extends { getState: () => infer T } ? T : never

type WithoutCallSignature<T> = { [K in keyof T]: T[K] }

/**
 * @deprecated Use `createStore` and `useStore` for context usage
 */
function createContext<S extends StoreApi<unknown>>() {
  if (import.meta.env?.MODE !== 'production') {
    console.warn(
      "[DEPRECATED] `context` will be removed in a future version. Instead use `import { createStore, useStore } from 'zustand'`. See: https://github.com/pmndrs/zustand/discussions/1180."
    )
  }
  const ZustandContext = reactCreateContext<S | undefined>(undefined)

  const Provider = ({
    createStore,
    children,
  }: {
    createStore: () => S
    children: ReactNode
  }) => {
    const storeRef = useRef<S>()

    if (!storeRef.current) {
      storeRef.current = createStore()
    }

    return createElement(
      ZustandContext.Provider,
      { value: storeRef.current },
      children
    )
  }

  const useContextStore: UseContextStore<S> = <StateSlice = ExtractState<S>>(
    selector?: (state: ExtractState<S>) => StateSlice,
    equalityFn?: (a: StateSlice, b: StateSlice) => boolean
  ) => {
    const store = useContext(ZustandContext)
    if (!store) {
      throw new Error(
        'Seems like you have not used zustand provider as an ancestor.'
      )
    }
    return useStoreWithEqualityFn(
      store,
      selector as (state: ExtractState<S>) => StateSlice,
      equalityFn
    )
  }

  const useStoreApi = () => {
    const store = useContext(ZustandContext)
    if (!store) {
      throw new Error(
        'Seems like you have not used zustand provider as an ancestor.'
      )
    }
    return useMemo<WithoutCallSignature<S>>(() => ({ ...store }), [store])
  }

  return {
    Provider,
    useStore: useContextStore,
    useStoreApi,
  }
}
'''

diff_code = '''return createElement(
      ZustandContext.Provider,
      { value: storeRef.current },
      children
    )
    '''


def get_embedding(text: List[str] | str) -> np.ndarray:

    flag_model = FlagModel('models/BAAI/bge-large-zh-v1.5',
                           query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                           use_fp16=False)

    return flag_model.encode(text)


limit = 1
# threshold = 0.8


def similarity_search(text):
    query_vector = get_embedding(text)
    hits = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
    )
    context = ''
    for item in hits:
        context = item.payload['page_content']
        # print("Id:", item.id)
        # print("Version:", item.version)
        # print("Payload:", item.payload)
        print("Score:", item.score)
        print("Payload metadata:", item.payload['metadata'])
        print("---")  # 用于分隔每个字典
    return context


def create_summary_prompt(language: str, source_code: str):
    prefix = "user: "
    suffix = "assistant(用中文): let's think step by step."
    return f"""{prefix}根据这段 {language} 代码，列出关于这段 {language} 代码用到的工具库、模块包。
  {language} 代码:
  ```{language}
  {source_code}
  ```
  请注意：
  - 知识列表中的每一项都不要有类似或者重复的内容
  - 列出的内容要和代码密切相关
  - 最少列出 3 项, 最多不要超过 6 项
  - 知识列表中的每一项要具体
  - 列出列表，不要对工具库、模块做解释
  {suffix}"""


def create_code_review_prompt(language: str, context: str, diff_code: str):
    return f"""user: 【指令】请根据所提供的上下文信息来审查变更代码，有任何错误或缺陷请指出，没有则输出“无”。
【已知信息】：{context}

【变更代码】：
```{language}
{diff_code}
```

assistant: """


def summarize(summary_prompt: str):
    resp = requests.post(
        url=llm_origin,
        json={
            "prompt": summary_prompt,
        },
        headers={
            'Content-Type': 'application/json;charset=utf-8'
        },
    )
    return resp.json()['response']


def code_review(code_review_prompt: str):
    resp = requests.post(
        url=llm_origin,
        json={
            "prompt": code_review_prompt,
        },
        headers={
            'Content-Type': 'application/json;charset=utf-8'
        },
    )
    return resp.json()['response']


if __name__ == "__main__":
    print('源码：', source_code)
    print('----------------------------------------------------------------')
    summary_prompt = create_summary_prompt('Typescript', source_code)
    print('summary prompt：', summary_prompt)
    print('----------------------------------------------------------------')
    summary = summarize(summary_prompt)
    print('总结：', summary)
    print('----------------------------------------------------------------')
    context = similarity_search(summary)
    print('上下文：', context)
    print('----------------------------------------------------------------')
    code_review_prompt = create_code_review_prompt(
        'Typescript', context, diff_code)
    print('CR prompt：', code_review_prompt)
    print('----------------------------------------------------------------')
    result = code_review(code_review_prompt)
    print('结论：', result)
