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
      <Title>Temperature (K)</Title>
      <Abstract>Temperature (K) Heatmap</Abstract>
      <!-- FeatureTypeStyles describe how to render different features -->
      <!-- A FeatureTypeStyle for rendering rasters -->
      <FeatureTypeStyle>
        <Rule>
          <Name>rule1</Name>
          <Title>Temperature (K)</Title>
          <Abstract>Temperature (K) Heatmap</Abstract>
          <RasterSymbolizer>
            <Opacity>1.0</Opacity>
            <ColorMap extended="true">
                    <ColorMapEntry color="#000000" quantity="270.15"  opacity="0"/>

                    <ColorMapEntry color="#EA0BD8" quantity="270.150000001"  label="270.15 °K"/>
                    <ColorMapEntry color="#7E0BE9" quantity="273.15"  label="273.15 °K"/>
                    <ColorMapEntry color="#0B14E8" quantity="277.15"  label="277.15 °K"/>
                    <ColorMapEntry color="#0B8FE7" quantity="281.15"  label="281.15 °K"/>
                    <ColorMapEntry color="#0BE6C3" quantity="285.15"  label="285.15 °K"/>
                    <ColorMapEntry color="#0CE648" quantity="289.15"  label="289.15 °K"/>
                    <ColorMapEntry color="#49E50C" quantity="293.15"  label="293.15 °K"/>
                    <ColorMapEntry color="#C2E40C" quantity="297.15"  label="297.15 °K"/>
                    <ColorMapEntry color="#E38D0C" quantity="301.15"  label="301.15 °K"/>
                    <ColorMapEntry color="#E3140D" quantity="305.15"  label="305.15 °K"/>

                    <ColorMapEntry color="#000000" quantity="323.15"  opacity="0"/>
            </ColorMap>            
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
