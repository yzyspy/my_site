---
title: async 的使用：从 Promise 到 async/await
date: '2026-11-04'
description: 从返回类型和执行顺序理解 async/await，掌握错误处理、串行与并发，避开异步循环中的常见陷阱。
tags:
  - TypeScript
  - async-await
  - Promise
---

<p class="article-kicker">TYPESCRIPT 深入浅出 · 异步编程</p>

# async 的使用：从 Promise 到 async/await

<p class="article-lead">接口请求、文件读取、数据库查询都涉及等待。用 async/await 可以把这些步骤写成容易阅读的顺序代码，但仍需要理解 Promise、错误传播和任务之间的依赖。</p>

<p class="article-byline">发布于 2026-11-04 · 约 8 分钟</p>

## 1. async 改变了函数的返回类型

在函数前加上 `async`，返回值就通过 Promise 交给调用方。即使函数里直接返回一个数字，调用方拿到的也不是数字本身。TypeScript 会检查这个返回类型。[TypeScript 官方示例](https://www.typescriptlang.org/play/javascript/modern-javascript/async-await.ts.html)

```typescript
async function getAnswer(): Promise<number> {
  return 42;
}

async function main(): Promise<void> {
  const pending: Promise<number> = getAnswer();
  const answer: number = await pending;
  console.log(answer); // 42
}

main().catch(console.error);
```

函数返回 `Promise<T>`，`await` 后得到的值是 `T`。如果没有返回值，通常标注 `Promise<void>`。声明为 `async` 也不会让 CPU 密集计算自动转移到其他线程。

## 2. await 暂停的是当前函数

异步函数会先执行到第一个 `await`，让出执行机会后再继续。即使等待的 Promise 已经完成，后续语句也会在之后的微任务中恢复执行。[MDN：async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)

```typescript
async function printOrder(): Promise<void> {
  console.log("A");
  await Promise.resolve();
  console.log("B");
}

console.log("start");
const task = printOrder();
console.log("end");
task.catch(console.error);

// 输出顺序：start → A → end → B
```

因此，`await` 不是让整个程序停住等待。浏览器仍有机会处理其他任务；不过，如果在 `await` 前执行长时间同步循环，页面依然可能卡住。

本文把 `await` 放在 `async` 函数中。顶层 `await` 还要求模块语境，并取决于 TypeScript 编译选项和运行环境，不能在任意脚本中直接使用。

## 3. 用 try/catch 处理失败

`async` 函数中抛出的错误会让返回的 Promise 拒绝；等待一个被拒绝的 Promise，会在 `await` 处抛出错误。需要在合适的调用层处理失败。[MDN：async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)

下面的例子不需要真实接口，可以直接观察成功、失败与清理逻辑：

```typescript
async function loadMessage(shouldFail: boolean): Promise<string> {
  if (shouldFail) {
    throw new Error("消息加载失败");
  }
  return "你好，TypeScript";
}

async function showMessage(): Promise<void> {
  try {
    const message = await loadMessage(true);
    console.log(message);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
  } finally {
    console.log("关闭加载状态");
  }
}

showMessage().catch(console.error);
```

这里的 `await` 很关键。如果只调用 `loadMessage(true)`，却没有等待或返回它，外层的 `try/catch` 无法捕获这个 Promise 的拒绝。`void loadMessage(true)` 也不会自动处理错误。

对于 `fetch`，还要检查 `response.ok`：HTTP 404、500 等状态不会仅因状态码就让 `fetch` 返回的 Promise 拒绝。[MDN：Using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

## 4. 有依赖用串行，互不依赖用并发

先定义一个模拟异步任务，后面的示例都复用它：

```typescript
function delay<T>(value: T, ms: number): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), ms);
  });
}
```

**串行**适合后一步依赖前一步的情况：

```typescript
async function loadProfile(): Promise<void> {
  const user = await delay({ id: 7, name: "小杨" }, 100);
  const posts = await delay([`用户 ${user.id} 的文章`], 100);
  console.log(user.name, posts);
}

loadProfile().catch(console.error);
```

**并发**适合相互独立的任务。先发起两个任务，再用 `Promise.all` 等待结果；结果数组按传入顺序排列，而不是按完成顺序排列。[MDN：Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)

```typescript
async function loadDashboard(): Promise<void> {
  const [profile, stats] = await Promise.all([
    delay({ name: "小杨" }, 200),
    delay({ articles: 4 }, 100),
  ]);

  console.log(profile.name, stats.articles);
}

loadDashboard().catch(console.error);
```

`Promise.all` 中任意任务拒绝，组合 Promise 就会拒绝，但它不会自动取消其他已启动的任务。需要拿到每个任务的成功或失败结果时，可以用 `Promise.allSettled`。[MDN：Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)

并发也不等于无限制发请求。对于大量数据，应按服务的限流要求分批处理，避免一次启动过多任务。

## 5. 不要用 forEach 等待异步任务

`forEach` 不会收集或等待回调返回的 Promise，下面的“全部完成”会提前输出。即使写成 `await ids.forEach(...)`，也解决不了这个问题，因为 `forEach` 返回的是 `undefined`。[MDN：Array.prototype.forEach](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach)

```typescript
// 反例：复用上一节的 delay，观察输出顺序。
const ids = [1, 2, 3];

ids.forEach(async (id) => {
  await delay(id, 100);
  console.log("已保存", id);
});

console.log("全部完成"); // 实际上还没完成
```

按顺序执行时，使用 `for...of`：

```typescript
async function saveInOrder(): Promise<void> {
  for (const id of [1, 2, 3]) {
    await delay(id, 100);
    console.log("已保存", id);
  }
  console.log("全部完成");
}

saveInOrder().catch(console.error);
```

允许并发时，使用 `map` 返回 Promise 数组，再统一等待：

```typescript
async function saveTogether(): Promise<void> {
  const savedIds = await Promise.all(
    [1, 2, 3].map((id) => delay(id, 100)),
  );
  console.log("全部完成", savedIds);
}

saveTogether().catch(console.error);
```

## 6. 运行这些示例

将要验证的代码放到 [TypeScript Playground](https://www.typescriptlang.org/play/)，打开 `strict` 检查后运行即可。运行第 4、5 节的示例时，把 `delay` 定义一并复制进去；各段示例建议分别运行，避免多个入口的日志交错。

写异步代码前，先确定三个问题：这个函数最终交付什么类型的值，后续步骤依赖哪些结果，失败应该由哪一层处理。把这三点写清楚，`async/await` 的结构通常就会自然明确。

## 延伸阅读

- [TypeScript 官方：Async Await 示例](https://www.typescriptlang.org/play/javascript/modern-javascript/async-await.ts.html)
- [MDN：async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [MDN：Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)
- [MDN：forEach 的异步回调说明](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach)
