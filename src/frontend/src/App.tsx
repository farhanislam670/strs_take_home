import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import PropertyList from "./pages/PropertyList";
import PropertyAnalysis from "./pages/PropertyAnalysis";
import TopPerformers from "./pages/TopPerformers";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/properties" element={<PropertyList />} />
        <Route path="/analysis/:propertyId" element={<PropertyAnalysis />} />
        <Route path="/top-performers" element={<TopPerformers />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
