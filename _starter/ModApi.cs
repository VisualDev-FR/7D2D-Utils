using System.Reflection;

namespace Harmony
{
    public class @MODNAME!pascal : IModApi
    {
        public void InitMod(Mod _modInstance)
        {
            var harmony = new HarmonyLib.Harmony(_modInstance.Name);
            harmony.PatchAll(Assembly.GetExecutingAssembly());
        }
    }
}