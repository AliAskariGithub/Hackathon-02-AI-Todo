import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface TestimonialCardProps {
  name: string;
  email: string;
  rating: number;
  message: string;
}

export default function TestimonialCard({ name, email, rating, message }: TestimonialCardProps) {
  return (
    <Card className="h-full border-border/40 bg-background/60 backdrop-blur-md shadow-sm hover:shadow-md transition-all duration-300 group relative overflow-hidden rounded-2xl">
      <CardContent className="p-6 flex flex-col h-full">
        {/* Rating Stars */}
        <div className="flex items-center gap-1 mb-4">
          {[...Array(5)].map((_, i) => (
            <svg
              key={i}
              className={cn(
                "w-4 h-4",
                i < rating ? "text-yellow-400 fill-yellow-400" : "text-muted/20"
              )}
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          ))}
        </div>

        {/* Message */}
        <div className="mb-6 flex-grow">
          <p className="text-base text-muted-foreground leading-relaxed">
            &quot;{message}&quot;
          </p>
        </div>

        {/* User Info */}
        <div className="flex items-center gap-3 mt-auto">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
            {name.charAt(0)}
          </div>
          <div>
            <p className="font-semibold text-sm text-foreground">{name}</p>
            <p className="text-xs text-muted-foreground">{email}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}