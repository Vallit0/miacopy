import React, { useState, useRef } from "react";
import Slider from "react-slick";
import InicioPage from "./InicioPage.jsx";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import Login from "./Login.jsx";
import Reports from "./Reports.jsx";

const Carousel = () => {
    const [activeIndex, setActiveIndex] = useState(0);
    const sliderRef = useRef(null);

    const pages = [
        <InicioPage/>, 
        <Login/>,
        <Reports/>,
    ];

    const settings = {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 1,
        slidesToScroll: 1,
        beforeChange: (current, next) => setActiveIndex(next),
    };

    return (
        <div>
            <Slider {...settings} ref={sliderRef}>
                {pages.map((page, index) => (
                    <div key={index}>{page}</div>
                ))}
            </Slider>
            <p>Active page: {activeIndex}</p>
        </div>
    );
};

export default Carousel;
