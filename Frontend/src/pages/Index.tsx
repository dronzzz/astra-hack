
import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import Features from '@/components/Features';
import HowItWorks from '@/components/HowItWorks';
import DemoShowcase from '@/components/DemoShowcase';
import TechStack from '@/components/TechStack';
import Footer from '@/components/Footer';

const Index = () => {
  return (
    <div className="min-h-screen bg-ai-dark overflow-x-hidden">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <DemoShowcase />
      <TechStack />
      <Footer />
    </div>
  );
};

export default Index;
