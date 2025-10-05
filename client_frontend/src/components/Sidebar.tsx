import React from 'react';
import type { Screen } from '../types';
import '../styles/Sidebar.css';
// import logoImage from '../assets/FMN_Flower.png';

interface SidebarProps {
  currentScreen: Screen;
  onScreenChange: (screen: Screen) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentScreen, onScreenChange }) => {
  return (
    <aside className="sidebar">
      <div className="brand">
        {/* <img src={logoImage} alt="ForgetMeNot Logo" title="ForgetMeNot Logo" /> */}
        <span style={{ fontSize: '14px', fontWeight: 'bold' }}>FMN</span>
      </div>
      <nav className="nav">
        <div className="nav-main">
          <button
            className={`nav-item ${currentScreen === 'dashboard' ? 'active' : ''}`}
            onClick={() => onScreenChange('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-item ${currentScreen === 'remember' ? 'active' : ''}`}
            onClick={() => onScreenChange('remember')}
          >
            Remember
          </button>
          <button
            className={`nav-item ${currentScreen === 'My_Memories' ? 'active' : ''}`}
            onClick={() => onScreenChange('My_Memories')}
          >
            My Memories
          </button>
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;
