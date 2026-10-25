"use client";

import { useEffect, useState } from "react";
import { LandmarkPOI } from "@/lib/types";
import { MapPin, Sparkles, Navigation2, Locate, Footprints } from "lucide-react";

interface MapViewProps {
  landmarks: LandmarkPOI[];
  selectedLandmark: LandmarkPOI | null;
  onSelectLandmark: (landmark: LandmarkPOI) => void;
  center: [number, number];
  zoom?: number;
  tourLandmarks?: LandmarkPOI[];
  onToggleTourLandmark?: (landmark: LandmarkPOI) => void;
  tourMode?: boolean;
}

export default function MapView({
  landmarks,
  selectedLandmark,
  onSelectLandmark,
  center,
  zoom = 14,
  tourLandmarks = [],
  onToggleTourLandmark,
  tourMode = false
}: MapViewProps) {
  const [isClient, setIsClient] = useState(false);
  const [MapComponents, setMapComponents] = useState<any>(null);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [locating, setLocating] = useState<boolean>(false);

  useEffect(() => {
    setIsClient(true);
    Promise.all([
      import("react-leaflet"),
      import("leaflet")
    ]).then(([ReactLeaflet, L]) => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      const createCustomIcon = (category: string, isSelected: boolean, tourIndex: number = -1) => {
        let color = "#06b6d4";
        if (category.includes("worship_hindu")) color = "#f59e0b";
        else if (category.includes("worship_christian")) color = "#3b82f6";
        else if (category.includes("museum")) color = "#a855f7";
        else if (category.includes("monument")) color = "#ec4899";
        else if (category.includes("historical")) color = "#10b981";

        const size = isSelected || tourIndex > 0 ? 38 : 28;
        const innerContent = tourIndex > 0
          ? `<span style="color: white; font-weight: bold; font-size: 13px; transform: rotate(45deg); display: block;">${tourIndex}</span>`
          : `<div style="width: ${size * 0.4}px; height: ${size * 0.4}px; background: white; border-radius: 50%; transform: rotate(45deg);"></div>`;

        const svgHtml = `
          <div style="
            background: ${tourIndex > 0 ? "#8b5cf6" : color};
            width: ${size}px;
            height: ${size}px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            border: 2px solid white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
          ">
            ${innerContent}
          </div>
        `;

        return L.divIcon({
          html: svgHtml,
          className: "custom-marker-icon",
          iconSize: [size, size],
          iconAnchor: [size / 2, size]
        });
      };

      // User location pulse icon
      const createUserLocationIcon = () => {
        const html = `
          <div style="position: relative; width: 24px; height: 24px;">
            <div style="position: absolute; width: 24px; height: 24px; background: #38bdf8; border-radius: 50%; opacity: 0.4; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
            <div style="position: absolute; top: 4px; left: 4px; width: 16px; height: 16px; background: #0284c7; border: 2px solid white; border-radius: 50%; box-shadow: 0 2px 6px rgba(0,0,0,0.4);"></div>
          </div>
        `;
        return L.divIcon({
          html,
          className: "user-loc-icon",
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        });
      };

      setMapComponents({
        MapContainer: ReactLeaflet.MapContainer,
        TileLayer: ReactLeaflet.TileLayer,
        Marker: ReactLeaflet.Marker,
        Popup: ReactLeaflet.Popup,
        Polyline: ReactLeaflet.Polyline,
        useMap: ReactLeaflet.useMap,
        createCustomIcon,
        createUserLocationIcon
      });
    });
  }, []);

  if (!isClient || !MapComponents) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-950 text-slate-400 gap-3">
        <Navigation2 className="w-8 h-8 text-cyan-400 animate-spin" />
        <span className="text-sm font-medium">Initializing OpenStreetMap Engine...</span>
      </div>
    );
  }

  const { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, createCustomIcon, createUserLocationIcon } = MapComponents;

  function MapController({ targetCenter }: { targetCenter: [number, number] }) {
    const map = useMap();
    useEffect(() => {
      map.flyTo(targetCenter, map.getZoom(), { duration: 1.2 });
    }, [targetCenter, map]);
    return null;
  }

  const handleLocateMe = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords: [number, number] = [pos.coords.latitude, pos.coords.longitude];
        setUserLocation(coords);
        setLocating(false);
      },
      (err) => {
        console.warn("Geolocation denied or unavailable:", err.message);
        setLocating(false);
      },
      { timeout: 10000 }
    );
  };

  // Route polyline coordinates connecting tour stops
  const tourPolyline = tourLandmarks.map((l) => [l.latitude, l.longitude] as [number, number]);

  return (
    <div className="relative w-full h-full rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
      <MapContainer
        center={userLocation || center}
        zoom={zoom}
        scrollWheelZoom={true}
        style={{ width: "100%", height: "100%" }}
      >
        <MapController targetCenter={userLocation || center} />
        
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {/* Tour Route Polyline */}
        {tourPolyline.length >= 2 && (
          <Polyline
            positions={tourPolyline}
            color="#8b5cf6"
            weight={4}
            opacity={0.8}
            dashArray="8, 6"
          />
        )}

        {/* User Geolocation Marker */}
        {userLocation && (
          <Marker position={userLocation} icon={createUserLocationIcon()}>
            <Popup>
              <div className="p-1 text-xs">
                <strong>Your Current Location</strong>
                <p className="text-[11px] text-slate-400">Autonomous proximity scanning active</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Landmark Markers */}
        {landmarks.map((poi) => {
          const isSelected = selectedLandmark?.id === poi.id;
          const tourIdx = tourLandmarks.findIndex((t) => t.id === poi.id);
          const tourOrderNumber = tourIdx >= 0 ? tourIdx + 1 : -1;

          return (
            <Marker
              key={poi.id}
              position={[poi.latitude, poi.longitude]}
              icon={createCustomIcon(poi.category, isSelected, tourOrderNumber)}
              eventHandlers={{
                click: () => {
                  if (tourMode && onToggleTourLandmark) {
                    onToggleTourLandmark(poi);
                  } else {
                    onSelectLandmark(poi);
                  }
                }
              }}
            >
              <Popup>
                <div className="p-1 max-w-[220px]">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                      {poi.category.replace("_", " ")}
                    </span>
                    {poi.distance_meters && (
                      <span className="text-[10px] text-slate-400">
                        {poi.distance_meters > 1000
                          ? `${(poi.distance_meters / 1000).toFixed(1)} km`
                          : `${Math.round(poi.distance_meters)} m`}
                      </span>
                    )}
                  </div>
                  <h4 className="font-bold text-sm text-slate-100 leading-snug mb-1">
                    {poi.name}
                  </h4>
                  {poi.tags?.opening_hours && (
                    <p className="text-[11px] text-slate-300 mb-2 truncate">
                      🕒 {poi.tags.opening_hours}
                    </p>
                  )}
                  
                  {tourMode ? (
                    <button
                      onClick={() => onToggleTourLandmark && onToggleTourLandmark(poi)}
                      className={`w-full mt-1 py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors ${
                        tourOrderNumber > 0
                          ? "bg-purple-600 text-white"
                          : "bg-slate-800 text-purple-300 border border-purple-500/50"
                      }`}
                    >
                      <Footprints className="w-3.5 h-3.5" />
                      {tourOrderNumber > 0 ? `Stop #${tourOrderNumber} in Tour` : "Add to Walking Tour"}
                    </button>
                  ) : (
                    <button
                      onClick={() => onSelectLandmark(poi)}
                      className="w-full mt-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-xs font-medium shadow-md shadow-cyan-500/20 hover:opacity-90 transition-opacity"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      Explore with Agents
                    </button>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Floating Action Controls on Map */}
      <div className="absolute top-4 left-4 z-[400] flex items-center gap-2">
        <button
          onClick={handleLocateMe}
          disabled={locating}
          className="glass-card hover:bg-slate-800 text-slate-200 px-3 py-2 rounded-xl text-xs font-medium flex items-center gap-1.5 shadow-lg border border-slate-700/80 transition-colors"
          title="Locate me using browser GPS"
        >
          <Locate className={`w-3.5 h-3.5 text-cyan-400 ${locating ? "animate-spin" : ""}`} />
          <span>{locating ? "Locating..." : "Near Me"}</span>
        </button>
      </div>

      <div className="absolute top-4 right-4 z-[400] glass-card px-3 py-1.5 rounded-lg text-[11px] text-slate-300 flex items-center gap-2 pointer-events-none">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
        <span>{landmarks.length} OSM Landmarks Discovered</span>
      </div>
    </div>
  );
}
