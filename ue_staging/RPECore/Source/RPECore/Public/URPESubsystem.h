#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "URPESubsystem.generated.h"
#include "core/RPEngine.h"
#include "core/World.h"


/**
 * URPESubsystem
 *
 * Manages the RPE simulation instance.
 * Accessible from anywhere via GetGameInstance()->GetSubsystem<URPESubsystem>()
 */
UCLASS()
class RPECORE_API URPESubsystem : public UGameInstanceSubsystem {
  GENERATED_BODY()

public:
  virtual void Initialize(FSubsystemCollectionBase &Collection) override;
  virtual void Deinitialize() override;

  // Simulation Tick (to be called from an Actor or Timer)
  UFUNCTION(BlueprintCallable, Category = "RPE Simulation")
  void TickSimulation();

  // Load Simulation Data
  UFUNCTION(BlueprintCallable, Category = "RPE Simulation")
  bool LoadEcosystem(const FString &JsonContent);

  // Accessors for raw C++ engine (Use with care)
  RPE::RPEngine *GetEngine() const { return Engine.Get(); }
  RPE::World *GetWorldState() const { return WorldState.Get(); }

private:
  TSharedPtr<RPE::World> WorldState;
  TSharedPtr<RPE::RPEngine> Engine;

  // Helper to log stats
  void LogStats();
};
