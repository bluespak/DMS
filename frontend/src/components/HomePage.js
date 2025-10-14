import React from 'react';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="homepage">
      <header className="homepage-header">
        <nav className="navbar">
          <div className="nav-links">
            <a href="#home" className="nav-link active">홈</a>
            <a href="#login" className="nav-link">로그인</a>
            <a href="#signup" className="nav-link">회원가입</a>
            <a href="#pricing" className="nav-link">가격</a>
            <a href="#help" className="nav-link">도움말</a>
          </div>
        </nav>
      </header>

      <main className="homepage-main">
        <div className="hero-section">
          <h1 className="main-title">데드맨 스위치</h1>
          
          <section className="info-section">
            <h2>왜 필요한가요?</h2>
            <p>
              나쁜 일들은 일어납니다. 때로는 당신에게도 일어날 수 있습니다. 만약 어떤 일이 생긴다면, 
              주변 사람들이 걱정할 수도 있습니다. 당신이 어떻게 느끼는지 알고 있습니다. 
              당신이 전에 말하고 싶었던 것들이나 사랑한다고 말하고 싶었던 것들을 
              당신의 반려동물들이 즉시 보살핌을 받을 수 있도록 확실히 하세요.
            </p>
            <p>
              이를 위해서는 데드맨 스위치가 필요합니다.
            </p>
          </section>

          <section className="info-section">
            <h2>어떻게 작동하나요?</h2>
            <p>
              이것이 작동하는 방식입니다. 몇 개의 이메일을 작성하고 수신자를 선택합니다. 
              이 이메일들은 발송될 때까지 개인적으로 저장됩니다. 당신이 살아있다는 것을 보여주기 위해 
              링크를 클릭하라는 요청을 받게 됩니다. 만약 어떤 일이 당신에게 일어난다면, 
              당신의 스위치가 이메일을 보내고 당신이 작성한 이메일들을 지정한 수신자들에게 발송할 것입니다. 
              일종의 "전자 유언"이라고 할 수 있습니다.
            </p>
          </section>

          <section className="info-section">
            <h2>언제 발송되나요?</h2>
            <p>
              알림은 특정 간격으로 전송됩니다 (이메일, 텔레그램 또는 브라우저 푸시 알림). 
              하루에서 1년까지 원하는 간격을 설정할 수 있습니다. 기본적으로 알림은 월 단위로 설정되어 있고, 
              지난 달에 생존 신호를 보이지 않은 경우 메시지가 전송됩니다 
              (무료 계정은 하루 1회로 제한됨). 이러한 알림에 응답하지 않으면, 
              모든 메시지가 마지막 체크인으로부터 90일 후에 전송됩니다.
            </p>
          </section>

          <section className="info-section">
            <h2>얼마나 드나요?</h2>
            <p>
              지금은 최대 1명의 수신자와 함께 무료로 이메일을 추가할 수 있습니다. 
              <a href="#upgrade" className="upgrade-link">계정을 업그레이드</a>하면 
              프리미엄 기능으로 더 많은 메시지 추가가 가능합니다. 또한 Dead Man's Switch에서 
              사용자 정의 메시지 간격을 설정할 수 있고, 가능한 한 자주 알림을 받을 수 있습니다.
            </p>
          </section>

          <section className="info-section">
            <h2>비용은 얼마인가요?</h2>
            <p>
              아무것도 들지 않습니다. 정말 무료입니다. 다음 버튼을 사용하여 지금 바로 시작할 수 있습니다:
            </p>
          </section>

          <div className="cta-section">
            <button className="build-switch-btn">
              내 스위치 만들기
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomePage;