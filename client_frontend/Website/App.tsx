import Card from "./components/Card";
import "./App.css";

const App: React.FC = () => {
  return (
    <div className="app">
      <h1>ForgetMeNot Collection</h1>
      <div className="card-container">
        <Card
          title="Forget-Me-Not"
          description="A delicate flower symbolizing remembrance and true love."
          imageUrl="https://upload.wikimedia.org/wikipedia/commons/1/16/Myosotis_sylvatica_closeup.jpg"
        />
        <Card
          title="Sunflower"
          description="Bright, tall, and full of warmth — just like the sun."
          imageUrl="https://upload.wikimedia.org/wikipedia/commons/4/40/Sunflower_sky_backdrop.jpg"
        />
      </div>
    </div>
  );
};

export default App;