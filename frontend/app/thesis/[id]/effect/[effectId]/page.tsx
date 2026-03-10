"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";

export default function EffectRedirect() {
  const params = useParams();
  const router = useRouter();
  const thesisId = params.id as string;

  useEffect(() => {
    router.replace(`/thesis/${thesisId}`);
  }, [thesisId, router]);

  return null;
}
