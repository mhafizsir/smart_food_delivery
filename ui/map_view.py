"""Peta folium untuk lokasi dan rute (Team 2)."""
import folium
import streamlit as st
from streamlit_folium import st_folium


def build_map(service, route_path=None):
    graph = service.map
    coords = graph.coords
    if not coords:
        return None
    restaurants_at = {}
    for restaurant in service.restaurants:
        spot = graph.find(restaurant.location)
        if spot:
            if spot not in restaurants_at:
                restaurants_at[spot] = []
            restaurants_at[spot].append(restaurant.name)

    total_lat = 0.0
    total_lon = 0.0
    for lat, lon in coords.values():
        total_lat += lat
        total_lon += lon
    center = [total_lat / len(coords), total_lon / len(coords)]
    fmap = folium.Map(location=center, zoom_start=13, tiles="Esri.WorldGrayCanvas")
    for start, end, distance, minutes in graph.edges():
        if start in coords and end in coords:
            folium.PolyLine([coords[start], coords[end]], color="gray", weight=3, opacity=0.6,
                            tooltip=f"{start} - {end}: {distance:g} km, {minutes:g} menit").add_to(fmap)

    if route_path:
        points = [coords[name] for name in route_path if name in coords]
        if len(points) > 1:
            folium.PolyLine(points, color="#1E6B45", weight=7, opacity=0.9,
                            tooltip="Rute pengiriman").add_to(fmap)
            lats = [p[0] for p in points]
            lons = [p[1] for p in points]
            fmap.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(30, 30))

    for name, (lat, lon) in coords.items():
        if route_path and name == route_path[-1]:
            color, icon, label = "darkgreen", "flag", f"Tujuan: {name}"
        elif name in restaurants_at:
            color, icon, label = "orange", "cutlery", f"{name}: {', '.join(restaurants_at[name])}"
        elif graph.kinds.get(name) == "CUSTOMER":
            color, icon, label = "cadetblue", "home", name
        else:
            color, icon, label = "gray", "info-sign", name
        folium.Marker([lat, lon], tooltip=label, popup=label,
                      icon=folium.Icon(color=color, icon=icon)).add_to(fmap)
    return fmap


def show_map(service, route_path=None, key="map", height=480):
    fmap = build_map(service, route_path)
    if fmap is None:
        st.info("Peta masih kosong. Tambahkan lokasi di halaman Peta & Rute.")
    else:
        st_folium(fmap, key=key, height=height, use_container_width=True, returned_objects=[])


def path_km(graph, path):
    total = 0.0
    for a, b in zip(path, path[1:]):
        for edge in graph.adjacency[a]:
            if edge["to"] == b:
                total += edge["distance"]
                break
    return round(total, 2)
