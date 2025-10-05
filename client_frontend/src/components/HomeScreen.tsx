import React from 'react';
import type { OrbitItem } from '../types';
import '../styles/HomeScreen.css';
// import starIcon from '../assets/fav_icon_clicked.png';

const HomeScreen: React.FC = () => {
  const orbitItems: OrbitItem[] = [
    { label: 'Family', gradient: 'linear-gradient(45deg, #ff6b6b, #feca57)' },
    { label: 'Friends', gradient: 'linear-gradient(45deg, #48cae4, #023e8a)' },
    { label: 'Work', gradient: 'linear-gradient(45deg, #f72585, #b5179e)' },
    { label: 'Travel', gradient: 'linear-gradient(45deg, #2d6a4f, #52b788)' },
    { label: 'Hobbies', gradient: 'linear-gradient(45deg, #e76f51, #f4a261)' },
    { label: 'Health', gradient: 'linear-gradient(45deg, #8ecae6, #219ebc)' },
    { label: 'Learning', gradient: 'linear-gradient(45deg, #fb8500, #ffb703)' }
  ];

  const getOrbitPosition = (index: number, total: number) => {
    const angle = (index / total) * 360;
    const radians = (angle * Math.PI) / 180;
    const radius = 230;
    const x = Math.cos(radians) * radius;
    const y = Math.sin(radians) * radius;
    return {
      transform: `translate(${x}px, ${y}px)`,
      top: '50%',
      left: '50%',
      marginTop: '-60px',
      marginLeft: '-60px'
    };
  };

  return (
    <div className="screen active">
      <div className="header-bar">Dashboard</div>
      <div className="content">
        <div className="cards">
          <div className="card">
            <h2>Welcome to ForgetMeNot</h2>
            <p>Your personal memory assistant. Start by adding your first memory in the Remember section.</p>
          </div>
          <div className="card">
            <h2>Quick Stats</h2>
            <p>Memories: 0 • Categories: 7 • Last updated: Today</p>
          </div>
        </div>
        <div className="orbit-container">
          <div className="central-circle">
            {/* <img src={starIcon} alt="Central Star" /> */}
            <span style={{ color: 'white', fontSize: '32px' }}>★</span>
          </div>
          {orbitItems.map((item, index) => (
            <div
              key={item.label}
              className="orbit-item"
              style={getOrbitPosition(index, orbitItems.length)}
            >
              <div className="orbit-circle" style={{ background: item.gradient }}>
                {/* <img src={starIcon} alt={item.label} /> */}
                <span style={{ color: 'white', fontSize: '24px' }}>★</span>
                <div className="orbit-circle-label">{item.label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;
