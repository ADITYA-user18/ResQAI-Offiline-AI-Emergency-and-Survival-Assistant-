import { useEffect } from 'react';
import gsap from 'gsap';

export const useAnimations = () => {
  const animateHero = (heroRef, titleRef, subtitleRef, ctaRef) => {
    if (!heroRef.current) return;

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    tl.fromTo(heroRef.current, 
      { opacity: 0 }, 
      { opacity: 1, duration: 1.2 }
    );

    if (titleRef.current) {
      tl.fromTo(titleRef.current,
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8 },
        '-=0.8'
      );
    }

    if (subtitleRef.current) {
      tl.fromTo(subtitleRef.current,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8 },
        '-=0.6'
      );
    }

    if (ctaRef.current) {
      tl.fromTo(ctaRef.current,
        { scale: 0.9, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.6 },
        '-=0.4'
      );
    }
  };

  const animateStagger = (parentRef, selector, delay = 0.15) => {
    if (!parentRef.current) return;

    gsap.fromTo(
      parentRef.current.querySelectorAll(selector),
      { y: 40, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        stagger: delay,
        duration: 0.8,
        ease: 'power3.out',
      }
    );
  };

  const floatElement = (elRef, duration = 3, yValue = 10) => {
    if (!elRef.current) return;

    return gsap.to(elRef.current, {
      y: `-=${yValue}`,
      yoyo: true,
      repeat: -1,
      duration: duration,
      ease: 'sine.inOut',
    });
  };

  return {
    animateHero,
    animateStagger,
    floatElement,
  };
};
export default useAnimations;
