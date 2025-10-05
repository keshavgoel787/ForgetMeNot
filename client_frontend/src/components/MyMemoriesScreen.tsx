import React from 'react';

const MyMemoriesScreen: React.FC = () => {
  return (
    <div className="screen active">
      <div className="header-bar">My Memories</div>
      <div className="content">
        <div className="cards">
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <h2>Memory Alpha</h2>
            </div>
            <p>Your first memory with advanced features and functionality.</p>
          </div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <h2>Memory Beta</h2>
            </div>
            <p>Second memory focusing on user experience and design.</p>
          </div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <h2>Memory Gamma</h2>
            </div>
            <p>A collection of cherished moments and experiences.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyMemoriesScreen;
