#include "URPESubsystem.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "rules/ForestRules.h"
#include "utils/JsonLoader.h"


void URPESubsystem::Initialize(FSubsystemCollectionBase &Collection) {
  Super::Initialize(Collection);

  UE_LOG(LogTemp, Log, TEXT("RPE Subsystem Initializing..."));

  // 1. Create Core RPE Objects
  WorldState = MakeShared<RPE::World>();
  Engine = MakeShared<RPE::RPEngine>(*WorldState);
  Engine->setVerbose(false);

  // 2. Register Rules
  ForestRules::RegisterForestRules(*Engine);

  UE_LOG(LogTemp, Log, TEXT("RPE Engine Initialized and Rules Registered."));
}

void URPESubsystem::Deinitialize() {
  UE_LOG(LogTemp, Log, TEXT("RPE Subsystem Deinitializing..."));
  Engine.Reset();
  WorldState.Reset();
  Super::Deinitialize();
}

void URPESubsystem::TickSimulation() {
  if (Engine) {
    Engine->tick();

    // Optional: Log stats every few ticks
    if (WorldState->getCurrentTick() % 60 == 0) {
      LogStats();
    }
  }
}

bool URPESubsystem::LoadEcosystem(const FString &JsonContent) {
  if (!WorldState)
    return false;

  std::string StdJson = TCHAR_TO_UTF8(*JsonContent);
  bool bSuccess = Utils::JsonLoader::loadForestEcosystem(*WorldState, StdJson);

  if (bSuccess) {
    UE_LOG(LogTemp, Log,
           TEXT("Successfully loaded ecosystem with %llu entities."),
           WorldState->getEntities().size());
  } else {
    UE_LOG(LogTemp, Error, TEXT("Failed to parse ecosystem JSON."));
  }

  return bSuccess;
}

void URPESubsystem::LogStats() {
  if (!WorldState)
    return;

  // Example stat logging
  int ProducerCount = 0;
  int ConsumerCount = 0;

  for (const auto &Pair : WorldState->getEntities()) {
    if (Pair.second->getKind() == "producer")
      ProducerCount++;
    else if (Pair.second->getKind() == "consumer")
      ConsumerCount++;
  }

  UE_LOG(LogTemp, Log,
         TEXT("RPE Stats | Tick: %llu | Producers: %d | Consumers: %d"),
         WorldState->getCurrentTick(), ProducerCount, ConsumerCount);
}
