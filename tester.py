#:import MDSwiper kivymd.uix.swiper.MDSwiper
#:import MDLabel kivymd.uix.label.MDLabel
#:import MDSwiperItem kivymd.uix.swiper.MDSwiperItem
#:import FitImage kivymd.uix.fitimage.FitImage
<MySwiper@MDGridLayout>
	rows: 2
	MyImage:
		id: img2
		keep_ratio: True
		allow_stretch: True
		width: self.parent.width
		size_hint_x: 1
		size_hint_y: 1
	Label:
		id: label2
	    color: 0, 0, 0, 1
		size: (400, 100)
        text_size:(400, None)
	
MDGridLayout:
	rows: 2
	MDScrollView:
		id:scroller
		MDList:
			id:swiper