import requests


def create_prompt(language: str, source_code: str):
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
  - 最少列出 3 个, 最多不要超过 6 个
  - 知识列表中的每一项要具体
  - 列出列表，不要对工具库、模块做解释
  - 输出中文
  {suffix}"""


def summary(source_code: str):
    resp = requests.post(
        url='http://127.0.0.1:8000',
        json={
            "prompt": create_prompt('Typescript', source_code),
        },
        headers={
            'Content-Type': 'application/json;charset=utf-8'
        },
    )
    return resp.json()['response'], resp.json()['history']


if __name__ == "__main__":
    response, history = summary('''
import {
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

export default createContext
  ''')
    print(response)
