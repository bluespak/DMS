// React 라이브러리에서 React를 가져옵니다
import React from 'react';

// React 18부터 사용하는 createRoot를 가져옵니다
import { createRoot } from 'react-dom/client';

// 우리가 만들 메인 App 컴포넌트를 가져옵니다
import App from './App';

// HTML의 id="root" 요소를 찾습니다
const container = document.getElementById('root');

// React 18 방식으로 root를 생성합니다
const root = createRoot(container);

// App 컴포넌트를 화면에 렌더링합니다
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);