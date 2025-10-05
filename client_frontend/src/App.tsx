import { useState } from 'react';
import type { Screen } from './types';
import Sidebar from './components/Sidebar';
import HomeScreen from './components/HomeScreen';
import RememberScreen from './components/RememberScreen';
import MyMemoriesScreen from './components/MyMemoriesScreen';
import './styles/App.css';

function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('dashboard');

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'dashboard':
        return <HomeScreen />;
      case 'remember':
        return <RememberScreen />;
      case 'My_Memories':
        return <MyMemoriesScreen />;
      default:
        return <HomeScreen />;
    }
  };

  return (
    <div className="app">
      <Sidebar currentScreen={currentScreen} onScreenChange={setCurrentScreen} />
      <main className="main">{renderCurrentScreen()}</main>
    </div>
  );
}

export default App
