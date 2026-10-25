"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import {
  Search, MapPin, Sparkles, SlidersHorizontal, ArrowRight, Layers, Compass, Loader2,
  Footprints, Route, Check, AlertCircle, Radio, Navigation
} from "lucide-react";
import { LandmarkPOI } from "@/lib/types";
import { searchLocations, getNearbyLandmarks, startExploration, planWalkingTour } from "@/lib/api";

const MapView = dynamic(() => import("@/components/MapView"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[450px] flex items-center justify-center bg-slate-950/70 rounded-2xl border border-slate-800 text-slate-400">
      <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
    </div>
  ),
});

export default function ExplorePage() {
  const router = useRouter();

  // Map & Discovery State
  const [searchQuery, setSearchQuery] = useState("Chennai, India");
  const [mapCenter, setMapCenter] = useState<[number, number]>([13.0827, 80.2707]);
  const [landmarks, setLandmarks] = useState<LandmarkPOI[]>([]);
  const [selectedLandmark, setSelectedLandmark] = useState<LandmarkPOI | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [loadingPOIs, setLoadingPOIs] = useState<boolean>(true);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  // Agent Configuration State
  const [duration, setDuration] = useState<number>(90);
  const [style, setStyle] = useState<string>("documentary");
  const [language, setLanguage] = useState<string>("en");
  const [isLaunching, setIsLaunching] = useState<boolean>(false);

  // Autonomous Walking Tour & Proximity Simulation State
  const [tourMode, setTourMode] = useState<boolean>(false);
  const [tourLandmarks, setTourLandmarks] = useState<LandmarkPOI[]>([]);
  const [isPlanningTour, setIsPlanningTour] = useState<boolean>(false);
  const [proximityAlert, setProximityAlert] = useState<string | null>(null);

  // Fetch nearby POIs whenever map center changes
  useEffect(() => {
    let active = true;
    setLoadingPOIs(true);
    getNearbyLandmarks(mapCenter[0], mapCenter[1], 3000)
      .then((data) => {
        if (active) {
          setLandmarks(data);
          if (data.length > 0 && !selectedLandmark) {
            setSelectedLandmark(data[0]);
          }
          setLoadingPOIs(false);
        }
      })
      .catch((err) => {
        console.error("Error loading POIs", err);
        if (active) setLoadingPOIs(false);
      });
    return () => {
      active = false;
    };
  }, [mapCenter]);

  // Handle City / Location Search
  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const results = await searchLocations(searchQuery);
      if (results.length > 0) {
        const top = results[0];
        setMapCenter([top.latitude, top.longitude]);
      }
    } finally {
      setIsSearching(false);
    }
  };

  // Launch Single-Landmark LangGraph Workflow
  const handleStartExploration = async () => {
    if (!selectedLandmark) return;
    setIsLaunching(true);
    try {
      const result = await startExploration({
        landmark_id: selectedLandmark.id,
        landmark_name: selectedLandmark.name,
        latitude: selectedLandmark.latitude,
        longitude: selectedLandmark.longitude,
        category: selectedLandmark.category,
        language,
        story_style: style,
        duration_seconds: duration,
        generate_audio: true
      });
      router.push(`/workspace?session_id=${result.session_id}`);
    } catch (err) {
      console.error("Failed to start exploration", err);
      setIsLaunching(false);
    }
  };

  // Toggle landmark in multi-stop Walking Tour
  const handleToggleTourLandmark = (landmark: LandmarkPOI) => {
    setTourLandmarks((prev) => {
      const exists = prev.some((l) => l.id === landmark.id);
      if (exists) {
        return prev.filter((l) => l.id !== landmark.id);
      } else {
        if (prev.length >= 5) {
          alert("Walking tours are limited to 5 stops for optimal pedestrian pacing.");
          return prev;
        }
        return [...prev, landmark];
      }
    });
  };

  // Launch Multi-Stop Walking Tour Planner
  const handleGenerateWalkingTour = async () => {
    if (tourLandmarks.length < 2) return;
    setIsPlanningTour(true);
    try {
      const tourRes = await planWalkingTour({
        landmarks: tourLandmarks,
        title: `${searchQuery.split(",")[0]} Curated Heritage Trail`,
        theme: "historical"
      });
      // Start exploration session for tour
      const sess = await startExploration({
        landmark_id: tourRes.tour_id,
        landmark_name: tourRes.title,
        latitude: tourLandmarks[0].latitude,
        longitude: tourLandmarks[0].longitude,
        category: "walking_tour",
        language,
        story_style: style,
        duration_seconds: 120,
        generate_audio: true
      });
      router.push(`/story?session_id=${sess.session_id}`);
    } catch (err) {
      console.error("Failed planning tour", err);
      setIsPlanningTour(false);
    }
  };

  // Simulate Autonomous Proximity Geofence Trigger (PRD Section 3)
  const handleSimulateProximity = () => {
    if (landmarks.length > 0) {
      const target = landmarks[0];
      setSelectedLandmark(target);
      setProximityAlert(`Proximity Alert: You entered the 250m radius of ${target.name}! Agents ready to narrate.`);
      setTimeout(() => setProximityAlert(null), 8000);
    }
  };

  const filteredLandmarks = selectedCategory === "all"
    ? landmarks
    : landmarks.filter((l) => l.category.toLowerCase().includes(selectedCategory.toLowerCase()));

  const categories = [
    { id: "all", label: "All Landmarks" },
    { id: "heritage", label: "Heritage" },
    { id: "museum", label: "Museums" },
    { id: "worship", label: "Places of Worship" },
    { id: "monument", label: "Monuments" }
  ];

  return (
    <div className="space-y-6">
      {/* Proximity Geofence Notification Banner */}
      {proximityAlert && (
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-cyan-950/90 border border-cyan-500/60 text-cyan-200 text-xs shadow-lg animate-bounce">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span className="font-medium">{proximityAlert}</span>
          </div>
          <button
            onClick={() => handleStartExploration()}
            className="px-2.5 py-1 rounded-md bg-cyan-600 hover:bg-cyan-500 text-white font-semibold"
          >
            Trigger Narration
          </button>
        </div>
      )}

      {/* Search & Location Bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 glass-panel p-4 rounded-2xl border border-slate-800">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-96 flex items-center">
          <Search className="absolute left-3.5 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search city e.g. Chennai, Mumbai, Paris..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/80 focus:ring-1 focus:ring-cyan-500/50"
          />
          <button
            type="submit"
            disabled={isSearching}
            className="absolute right-2 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
          >
            {isSearching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Search"}
          </button>
        </form>

        <div className="flex items-center gap-2 w-full md:w-auto justify-between md:justify-end">
          {/* Walking Tour Toggle */}
          <button
            onClick={() => {
              setTourMode(!tourMode);
              if (!tourMode && landmarks.length >= 2) {
                setTourLandmarks([landmarks[0], landmarks[1]]);
              }
            }}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all border ${
              tourMode
                ? "bg-purple-600 text-white border-purple-400 shadow-md shadow-purple-500/25"
                : "bg-slate-900 text-slate-300 border-slate-800 hover:border-slate-700"
            }`}
          >
            <Footprints className="w-3.5 h-3.5" />
            <span>{tourMode ? "Walking Tour Mode ON" : "Walking Tour Mode"}</span>
          </button>

          {/* Simulate Geofence Button */}
          <button
            onClick={handleSimulateProximity}
            className="flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 transition-colors"
            title="Simulate entering a 250m landmark radius"
          >
            <Navigation className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">Simulate Geofence</span>
          </button>
        </div>
      </div>

      {/* POI Category Filters */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        {categories.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelectedCategory(c.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
              selectedCategory === c.id
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800"
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Main Grid: Interactive Map + Configuration Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[580px]">
        {/* Interactive Map (8 cols) */}
        <div className="lg:col-span-8 min-h-[450px] lg:min-h-full">
          <MapView
            landmarks={filteredLandmarks}
            selectedLandmark={selectedLandmark}
            onSelectLandmark={(poi) => setSelectedLandmark(poi)}
            center={mapCenter}
            zoom={14}
            tourMode={tourMode}
            tourLandmarks={tourLandmarks}
            onToggleTourLandmark={handleToggleTourLandmark}
          />
        </div>

        {/* Selected Landmark / Tour Planner Drawer (4 cols) */}
        <div className="lg:col-span-4 flex flex-col justify-between glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          {tourMode ? (
            /* Multi-Stop Walking Tour Mode Drawer */
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Route className="w-4 h-4 text-purple-400" />
                  <h3 className="font-bold text-base text-slate-100">Walking Tour Planner</h3>
                </div>
                <span className="text-[10px] font-mono text-purple-300 px-2 py-0.5 rounded bg-purple-950 border border-purple-800">
                  {tourLandmarks.length} Stops Selected
                </span>
              </div>

              <p className="text-xs text-slate-400">
                Click landmarks on the map to add stops. The Orchestrator will calculate walking legs, optimize the sequence, and generate a continuous trail guide.
              </p>

              {/* Waypoints List */}
              <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                {tourLandmarks.length === 0 ? (
                  <div className="p-4 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-xl">
                    Click landmarks on the map to add tour stops.
                  </div>
                ) : (
                  tourLandmarks.map((stop, idx) => (
                    <div
                      key={stop.id}
                      className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-purple-600 text-white font-bold text-[11px] flex items-center justify-center">
                          {idx + 1}
                        </span>
                        <span className="font-medium text-slate-200 truncate max-w-[170px]">
                          {stop.name}
                        </span>
                      </div>
                      <button
                        onClick={() => handleToggleTourLandmark(stop)}
                        className="text-slate-500 hover:text-red-400 text-xs px-1.5"
                      >
                        ✕
                      </button>
                    </div>
                  ))
                )}
              </div>

              {/* Tour Generation CTA */}
              <button
                onClick={handleGenerateWalkingTour}
                disabled={tourLandmarks.length < 2 || isPlanningTour}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-500 text-white font-semibold text-xs shadow-lg shadow-purple-500/20 hover:opacity-95 active:scale-98 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isPlanningTour ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Synthesizing Trail Story...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Intelligent Walking Tour ({tourLandmarks.length} stops)
                  </>
                )}
              </button>
            </div>
          ) : selectedLandmark ? (
            /* Single Landmark Exploration Drawer */
            <>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
                    {selectedLandmark.category.replace("_", " ")}
                  </span>
                  {selectedLandmark.distance_meters && (
                    <span className="text-xs text-slate-400">
                      {Math.round(selectedLandmark.distance_meters)} meters away
                    </span>
                  )}
                </div>

                <h3 className="text-xl font-bold text-slate-100 leading-tight">
                  {selectedLandmark.name}
                </h3>

                <p className="text-xs text-slate-400">
                  {selectedLandmark.tags?.wikipedia
                    ? `Archived in Wikipedia: ${selectedLandmark.tags.wikipedia}`
                    : "Tagged as a cultural heritage landmark in OpenStreetMap."}
                </p>

                {selectedLandmark.tags?.opening_hours && (
                  <div className="text-xs text-slate-300 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                    🕒 <strong>Hours:</strong> {selectedLandmark.tags.opening_hours}
                  </div>
                )}
              </div>

              {/* Story Configuration Controls */}
              <div className="space-y-4 pt-3 border-t border-slate-800">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <SlidersHorizontal className="w-3.5 h-3.5 text-cyan-400" />
                  Story Configuration
                </h4>

                <div>
                  <label className="text-xs text-slate-400 mb-1.5 block">Narration Duration</label>
                  <div className="grid grid-cols-3 gap-2">
                    {[60, 90, 120].map((sec) => (
                      <button
                        key={sec}
                        onClick={() => setDuration(sec)}
                        className={`py-1.5 rounded-lg text-xs font-medium transition-all ${
                          duration === sec
                            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50"
                            : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                        }`}
                      >
                        {sec}s
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-400 mb-1.5 block">Narration Style</label>
                  <div className="grid grid-cols-3 gap-2">
                    {["documentary", "conversational", "educational"].map((s) => (
                      <button
                        key={s}
                        onClick={() => setStyle(s)}
                        className={`py-1.5 rounded-lg text-xs capitalize font-medium transition-all ${
                          style === s
                            ? "bg-purple-500/20 text-purple-300 border border-purple-500/50"
                            : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                        }`}
                      >
                        {s.slice(0, 7)}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-400 mb-1.5 block">Language</label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full py-2 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="en">English</option>
                    <option value="ta">Tamil (தமிழ்)</option>
                    <option value="te">Telugu (తెలుగు)</option>
                    <option value="hi">Hindi (हिन्दी)</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleStartExploration}
                disabled={isLaunching}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 hover:opacity-95 active:scale-98 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLaunching ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Launching LangGraph...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Launch 4-Agent Story Workflow
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </>
                )}
              </button>
            </>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-3">
              <Compass className="w-12 h-12 text-slate-600 animate-pulse" />
              <h4 className="font-semibold text-sm text-slate-300">Select a Landmark on Map</h4>
              <p className="text-xs text-slate-500">
                Click any marker on OpenStreetMap to configure the agents, or switch to Walking Tour Mode to plan a trail.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
