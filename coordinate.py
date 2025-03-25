import uiautomator2 as u2

d = u2.connect()  # Connect to the phone via ADB
d.screenshot("start_screen.png")  # Take a screenshot (optional)

# Get the bounds of the DC vs LSG block (change text if needed)
element = d(text="₹49")  # Locate by text
if element.exists:
    bounds = element.info['bounds']
    x_center = (bounds['left'] + bounds['right']) // 2
    y_center = (bounds['top'] + bounds['bottom']) // 2
    print(f"DC vs LSG Block Coordinates: ({x_center}, {y_center})")
else:
    print("DC vs LSG block not found!")
