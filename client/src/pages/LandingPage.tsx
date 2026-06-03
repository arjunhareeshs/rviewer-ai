import { Navbar } from '../components/landing/Navbar';
import { HeroSection } from '../components/landing/HeroSection';
import { ResumeFlowSection } from '../components/landing/ResumeFlowSection';
import SmoothScrollProvider from '../providers/SmoothScrollProvider';

export default function LandingPage() {
  return (
    <SmoothScrollProvider>
      <div className="bg-cream min-h-screen">
        <Navbar />
        <main>
          <HeroSection />
          <ResumeFlowSection />
          {/* <FeaturesGrid /> */}
          {/* <StatsSection /> */}
          {/* <CTASection /> */}
        </main>
        {/* <Footer /> */}
      </div>
    </SmoothScrollProvider>
  );
}
