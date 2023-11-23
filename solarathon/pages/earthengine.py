import ee
import geemap

import solara

zoom = solara.reactive(4)
center = solara.reactive([40, -100])


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_basemap("Esri.WorldImagery")
        self.add_ee_data()
        self.add_layer_manager()
        self.add_inspector()

    def add_ee_data(self):
        # Add Earth Engine dataset
        dem = ee.Image('USGS/SRTMGL1_003')
        landsat7 = ee.Image('LANDSAT/LE7_TOA_5YEAR/1999_2003').select(
            ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']
        )
        states = ee.FeatureCollection("TIGER/2018/States")

        # New Sentinel code
        try:
            point = ee.Geometry.Point(77.6,28.5)
            d =  ee.ImageCollection("COPERNICUS/S2").select(["B8", "B4", "B3"]).filterBounds(point)

            sentinel = ee.Image(d.filterDate("2019-01-01","2019-10-01").sort("CLOUD_COVERAGE_ASSESSEMENT").first())
            
            self.addLayer(sentinel,{'bands': ["B8", "B4", "B3"], 'min': 0, 'max': 3000},'Sentinel',False,)

            ndvi = ee.Image(d.filterDate("2023-01-01","2023-10-01").sort("CLOUD_COVERAGE_ASSESSEMENT").first()).expression("(NIR - RED) / (NIR + RED)",{"NIR":sentinel.select("B8"), "RED":sentinel.select("B4")})
            #disp_ndvi  = display={"min":0,"max":1,"palette":[ 'red','orange', 'yellow','yellowgreen', 'green','black']}
            self.addLayer(ndvi,{"min":0,"max":1,"palette":[ 'red','orange', 'yellow','yellowgreen', 'green','black']},"NDVI",False,)

        except:
            print("Could not generate sentinel")

        # New example trial 
        try:
            roi =ee.Geometry.Polygon(
                    [[[59.402645607468386, 36.721247854081604],
                    [59.402645607468386, 6.293426486681035],
                    [100.18389560746839, 6.293426486681035],
                    [100.18389560746839, 36.721247854081604]]])

            d_2 = ee.ImageCollection('MODIS/006/MYD11A1').filter(ee.Filter.date('2021-01-01', '2021-04-30')).select('LST_Day_1km')

            clip=d_2.mean().clip(roi)     
            band = {'min': 13000.0, 'max': 16500.0, 'palette': ['#00007b','#0e50f6', '05fce0', '1cfe07', 'f2fc03', '#feaf11', '#f46f28','#fe4709',],}
            self.addLayer(clip, band,'LST',False,); 
        except:
            print("Temperature failure")

        # Set visualization parameters.
        vis_params = {
            'min': 0,
            'max': 4000,
            'palette': ['006633', 'E5FFCC', '662A00', 'D8D8D8', 'F5F5F5'],
        }

        # Add Earth Engine layers to Map
        self.addLayer(dem, vis_params, 'SRTM DEM', True, 0.5)
        self.addLayer(
            landsat7,
            {'bands': ['B4', 'B3', 'B2'], 'min': 20, 'max': 200, 'gamma': 2.0},
            'Landsat 7',
            False,
        )
        self.addLayer(states, {}, "US States",False,)

        

@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        # solara components support reactive variables
        # solara.SliderInt(label="Zoom level", value=zoom, min=1, max=20)
        # using 3rd party widget library require wiring up the events manually
        # using zoom.value and zoom.set
        Map.element(  # type: ignore
            zoom=zoom.value,
            on_zoom=zoom.set,
            center=center.value,
            on_center=center.set,
            scroll_wheel_zoom=True,
            add_google_map=True,
            height="700px",
        )
        solara.Text(f"Zoom: {zoom.value}")
        solara.Text(f"Center: {center.value}")