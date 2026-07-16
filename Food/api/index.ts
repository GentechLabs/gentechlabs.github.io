import { Router } from "@agentcash/router";
import { createServer } from "http";
import { z } from "zod";

const router = new Router();

// Cookbook — look up a dish you saved from travel
router
  .route("recipes")
  .paid("0.01")
  .body(z.object({ query: z.string() }))
  .handler(({ body }) => {
    return { recipes: [] };
  });

// Stores — find ingredients at your local Kroger
router
  .route("stores")
  .paid("0.01")
  .body(z.object({ dishId: z.string(), store: z.string().optional() }))
  .handler(({ body }) => {
    return { store: {}, total: "$12-15", deals: [] };
  });

// Order — find + order via dd-cli or deliver
router
  .route("order")
  .paid("0.01")
  .body(z.object({
    query: z.string(),
    cuisine: z.string().optional(),
    maxPrice: z.number().optional(),
    useDeals: z.boolean().optional(),
  }))
  .handler(({ body }) => {
    // Check dd-cli for matching restaurants + deals
    return { results: [], bestDeal: null };
  });

// Work offset — earn delivery fee via WURK microtasks
router
  .route("offset")
  .paid("0.01")
  .body(z.object({ amount: z.number(), currency: z.string().default("usd") }))
  .handler(({ body }) => {
    // Calculate how many WURK tasks needed to offset
    const tasksNeeded = Math.ceil(body.amount / 0.50);
    return {
      tasksNeeded,
      suggestions: [
        { task: "Write 3 restaurant reviews", pay: 0.50, time: "5 min" },
        { task: "Vote on 10 menu designs", pay: 0.50, time: "3 min" },
      ],
    };
  });

// Deals — what's on sale at your store right now
router
  .route("deals")
  .paid("0.01")
  .body(z.object({ store: z.string().default("kroger") }))
  .handler(({ body }) => {
    return { deals: [], store: body.store };
  });

// Health
router
  .route("health")
  .unprotected()
  .handler(() => ({ status: "ok", version: "0.2.0" }));

const port = process.env.PORT || 3000;
createServer(router.fetch).listen(port, () => {
  console.log(`🍽️ GenTech Food v0.2.0 — cookbook + ordering + work offsets`);
  console.log(`   http://localhost:${port}/.well-known/x402`);
});
