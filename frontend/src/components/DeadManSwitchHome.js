import React from 'react';
import './DeadManSwitchHome.css';

const DeadManSwitchHome = ({ onCreateSwitch }) => {
  return (
    <div className="dms-home">
      {/* 헤더 */}
      <header className="dms-header">
        <h1 className="dms-title">데드맨 스위치</h1>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="dms-main">
        {/* 왜? 섹션 */}
        <section className="dms-section why-section">
          <h2 className="section-title">왜?</h2>
          <div className="section-content">
            <p>
              나쁜 일은 일어날 수 있습니다. 때로는 당신에게, 때로는 주변 사람들에게 말이죠. 
              만약 무언가 나쁜 일이 일어났을 때, 주변 사람들이 당신이 안전하지 않다는 것을 알 수 있도록 
              소중한 사람들에게 무언가를 남겨두고 싶을 수도 있습니다. 
              아니면 단순히 당신이 말하고 싶었던 것들을 전하고 싶을 수도 있습니다.
            </p>
            <p>그래서 데드맨 스위치가 필요합니다.</p>
            <p>이것은 당신의 반려동물이 제때 돌봄을 받을 수 있도록 확실히 해줍니다.</p>
          </div>
        </section>

        {/* 어떻게? 섹션 */}
        <section className="dms-section how-section">
          <h2 className="section-title">어떻게?</h2>
          <div className="section-content">
            <p>
              작동 방식은 이렇습니다. 몇 개의 이메일을 작성하고 수신자를 선택합니다. 
              이 이메일들은 발송될 때까지 비공개로 저장됩니다. 스위치는 정기적으로 
              (이메일, 텔레그램 또는 브라우저 푸시 알림을 통해) 당신에게 알림을 보내어 
              링크를 클릭하여 당신이 괜찮다는 것을 보여달라고 요청합니다. 
              만약 무언가 나쁜 일이 일어나 당신이 이러한 알림에 응답하지 못하면, 
              스위치가 작동하여 당신이 작성한 이메일들을 지정한 수신자들에게 발송합니다. 
              "전자 유언장"이라고 할 수 있겠네요.
            </p>
          </div>
        </section>

        {/* 언제? 섹션 */}
        <section className="dms-section when-section">
          <h2 className="section-title">언제?</h2>
          <div className="section-content">
            <p>
              알림은 특정 간격으로 전송됩니다 (이메일, 텔레그램 또는 브라우저 푸시 알림을 통해). 
              간격을 원하는 대로 설정할 수 있습니다 - 하루부터 3년까지. 기본값은 3일 후입니다. 
              생명의 징후를 보이지 않으면 (무료 계정은 1일로 제한), 이러한 알림에 응답하지 않으면 
              모든 메시지가 작성된 후 365일 후에 전송됩니다.
            </p>
          </div>
        </section>

        {/* 얼마나? 섹션 */}
        <section className="dms-section howmuch-section">
          <h2 className="section-title">얼마나?</h2>
          <div className="section-content">
            <p>
              현재는 최대 1개의 이메일과 1명의 수신자로 무료로 사용할 수 있습니다. 
              <a href="#upgrade" className="upgrade-link">계정을 업그레이드</a>하면 
              프리미엄으로 더 많은 메시지를 추가할 수 있습니다. 또한 데드맨 스위치에서 
              맞춤 메시징 간격을 설정할 수 있게 해주며, 가능한 한 자주 알림을 받을 수 있습니다.
            </p>
          </div>
        </section>

        {/* 하지만? 섹션 */}
        <section className="dms-section but-section">
          <h2 className="section-title">하지만?</h2>
          <div className="section-content">
            <p>
              하지만 아무것도 없습니다. 그냥 없어요. 지금 바로 시작할 수 있습니다. 
              아래 버튼을 사용하여 등록하기만 하면 됩니다:
            </p>
          </div>
        </section>

        {/* CTA 버튼 */}
        <div className="cta-section">
          <button className="build-switch-btn" onClick={onCreateSwitch}>
            내 스위치 만들기
          </button>
        </div>
      </main>

      {/* 푸터 */}
      <footer className="dms-footer">
        <p>&copy; 2025 Dead Man's Switch. 모든 권리 보유.</p>
      </footer>
    </div>
  );
};

export default DeadManSwitchHome;