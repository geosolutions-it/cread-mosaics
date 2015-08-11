<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0" 
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
 xmlns="http://www.opengis.net/sld" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 xmlns:xlink="http://www.w3.org/1999/xlink" 
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- a Named Layer is the basic building block of an SLD document -->
  <NamedLayer>
    <Name>default_raster</Name>
    <UserStyle>
    <!-- Styles can have names, titles and abstracts -->
      <Title>Temperature (C)</Title>
      <Abstract>Temperature (C) Heatmap</Abstract>
      <!-- FeatureTypeStyles describe how to render different features -->
      <!-- A FeatureTypeStyle for rendering rasters -->
      <FeatureTypeStyle>
        <Rule>
          <Name>rule1</Name>
          <Title>Temperature (C)</Title>
          <Abstract>Temperature (C) Heatmap</Abstract>
          <RasterSymbolizer>
            <Opacity>1.0</Opacity>
            <ColorMap extended="true">
                    <ColorMapEntry color="#000000" quantity="-50.0"  opacity="0"/>
                    <ColorMapEntry color="#EA0BD8" quantity="-32.0"  label="-32 °C"/>
                    <ColorMapEntry color="#AB0BE9" quantity="-20.0"  label="-20 °C"/>
                    <ColorMapEntry color="#5B0BE9" quantity="-16.0"  label="-16 °C"/>
                    <ColorMapEntry color="#0B0BE8" quantity="-12.0"  label="-12 °C"/>
                    <ColorMapEntry color="#0B5AE8" quantity="-8.0"   label="-8 °C"/>
                    <ColorMapEntry color="#0BAAE7" quantity="-4.0"   label="-4 °C"/>
                    <ColorMapEntry color="#0BE7D5" quantity="0.0"    label="0 °C"/>
                    <ColorMapEntry color="#0CE686" quantity="4.0"    label="4 °C"/>
                    <ColorMapEntry color="#0CE537" quantity="8.0"    label="8 °C"/>
                    <ColorMapEntry color="#2FE50C" quantity="12.0"   label="12 °C"/>
                    <ColorMapEntry color="#7DE50C" quantity="16.0"   label="16 °C"/>
                    <ColorMapEntry color="#CBE40C" quantity="20.0"   label="20 °C"/>
                    <ColorMapEntry color="#E4AF0C" quantity="24.0"   label="24 °C"/>
                    <ColorMapEntry color="#E3620C" quantity="28.0"   label="28 °C"/>
                    <ColorMapEntry color="#ff0000" quantity="32.0"   label="32 °C"/>
                    <ColorMapEntry color="#E3140D" quantity="50.0"   opacity="0"/>
            </ColorMap>            
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
