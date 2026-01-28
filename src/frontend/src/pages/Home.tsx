import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

export default function Home() {
  const navigate = useNavigate();
  const [propertyId, setPropertyId] = useState("");

  const handleAnalysisClick = () => {
    if (propertyId.trim()) {
      navigate(`/analysis/${propertyId.trim()}`);
    } else {
      alert("Please enter a Property ID");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Investment Property Dashboard
          </h1>
          <p className="text-xl text-gray-600">
            Analyze short-term rental properties and discover top opportunities
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-2xl">🏘️ Browse Properties</CardTitle>
              <CardDescription className="text-base">
                View all properties with filtering and sorting options
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full"
                onClick={() => navigate("/properties")}
              >
                Explore Properties
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-2xl">⭐ Top Performers</CardTitle>
              <CardDescription className="text-base">
                Discover the highest-rated investment opportunities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full"
                onClick={() => navigate("/top-performers")}
              >
                View Insights
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-2xl">📊 Property Analysis</CardTitle>
              <CardDescription className="text-base">
                Deep dive into property metrics and comparisons
              </CardDescription>
            </CardHeader>
            <CardContent>
              <input
                type="text"
                placeholder="Enter Property ID"
                value={propertyId}
                onChange={(e) => setPropertyId(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAnalysisClick()}
                className="w-full px-3 py-2 mb-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Button className="w-full" onClick={handleAnalysisClick}>
                Analyze Property
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
